from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
# Vulnerability 5, A05:2021 – Security Misconfiguration
# A fix would be to change below to:
# app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))
app.secret_key = 'super-secret-key-12345'

DATABASE = 'app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    conn.commit()
    conn.close()


@app.before_request
def ensure_db_initialized():
    if not app.config.get('DB_INITIALIZED'):
        init_db()
        app.config['DB_INITIALIZED'] = True

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

#Vulnerability 3, A02:2021 – Cryptographic Failures

#To fix uncomment comments down below (lines 88-95 and 115) and add this import:
#from werkzeug.security import generate_password_hash, check_password_hash



#Vulnerability 4, A07:2021 – Identification and Authentication Failures

#To fix add this:

#def validate_password_strength(password):
#    if len(password) < 8:
#        return False, "Password must be at least 8 characters"
#    if not any(c.isupper() for c in password):
#        return False, "Password must contain uppercase letter"
#    if not any(c.isdigit() for c in password):
#        return False, "Password must contain a number"
#    if not any(c in '!@#$%^&*' for c in password):
#        return False, "Password must contain special character"
#    return True, "OK"

#and uncomment commented lines down below:

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

          #Vulnerability 4
#        is_valid, message = validate_password_strength(password)
#        if not is_valid:
#            return message, 400

        conn = get_db_connection()
        #Vulnerability 3
        #password_hash = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password))
            #Also vulnerability 3
            #conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
#            (username, password_hash))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return 'Username already exists', 400
        finally:
            conn.close()

    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        #Vulnerability 3
        #if user and check_password_hash(user['password'], password):
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']

            return redirect(url_for('dashboard'))

        return 'Invalid username or password', 401

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC',
                        (user_id,)).fetchall()
    conn.close()

    return render_template('dashboard.html', notes=notes)

@app.route('/add-note', methods=['GET', 'POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        conn = get_db_connection()
        conn.execute('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)',
                    (user_id, title, content))
        conn.commit()
        conn.close()

        print(f"[DEBUG] User {session['username']} created note at {datetime.now()}")

        return redirect(url_for('dashboard'))

    return render_template('add_note.html')

# Vulnerability 1, A01:2021 – Broken Access Control

#To fix change below to:

@app.route('/note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    # note = conn.execute('SELECT * FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id'])).fetchone()
    #conn.close()
#     if note is None:
#         return 'Access denied or Note not found', 403

    conn.close()
    if note is None:
        return 'Note not found', 404
    return render_template('view_note.html', note=note)

# Also here below is the same vulnerability, A01:2021 – Broken Access Control
#To fix change to:

@app.route('/delete-note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))

    # note = conn.execute('SELECT * FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id'])).fetchone()
# if note is None:
#        conn.close()
#        return 'Access denied', 403

# conn.execute('DELETE FROM notes WHERE id = ? AND user_id = ?',
#              (note_id, session['user_id']))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
