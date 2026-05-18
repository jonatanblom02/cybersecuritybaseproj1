# Cyber Security Base project

A simple note app where users can write, add and delete notes.

### Startup Instructions:

1. Start by cloning the repository to a directory

2. Install Poetry in case you haven't already following these instructions:
https://python-poetry.org/docs/#installation

3. Install dependencies by doing `poetry install`

4. Activate the virtual environment with `poetry shell`

5. Run Flask application with `flask run`

6. Access the application in your web browser with `http://127.0.0.1:5000`


## OWASP 2021 5 vulnerabilities:

### Vulnerability 1

#### A01:2021 – Broken Access Control

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L170

and

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L187

A vulnerability for broken access control is the lack of inspecting whether a user owns a note or not. Before, any user was able to view and delete another user's notes simply by guessing the id of the note. The fix checks whether a user is the owner of the note.

In the screenshots we can see that both users alice and heips both see the same notes that are originally made by Alice. In the after photo when heips tries to access the note, their access is denied since the owner is Alice.

Appropriate fix would be to uncomment:
https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L168-171

and

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L189-195

### Vulnerability 2

#### A06:2021 - Vulnerable and Outdated Components

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/pyproject.toml#L10-11

Here we can find a vulnerability by using old flask and Werkzeug versions that has been classified as high risk. We can see this by installing a checker with `pip install pip-audit` and then doing `poetry export -f requirements.txt | pip-audit`.

In the before screenshot we can see warnings for the Werkzeug version used.

The fix is to change the flask version to a more recent, safe one:

`version = "3.1.3"` (The Werkzeug version doesn't need to be specified since Flask installs the latest secure one automatically) and then running `poetry update`

The after screenshots show that the Werkzeug warnings disappear after changing to a newer version of flask and Werkzeug when doing the same command `poetry export -f requirements.txt | pip-audit`.


### Vulnerability 3

#### A02:2021 – Cryptographic Failures

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L91-92

Here a serious vulnerability is storing the password as itself without hashing it. Incase attackers would have access to the database they would immediately get access to all users passwords.

In the screenshot we can see that this is possible in terminal by first doing `sqlite3 app.db` and then the query `SELECT username, password FROM users;`. By doing this we see a list of all users and their passwords.

The fix is to use a default hashing by for example Werkzeug library which prolongs cracking of individual passwords.

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L55
https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L88-95

In the screenshots we first see a list of users and their passwords but after making the changes and deleting the old database and making a new user, we can now see the password for the user is hashed.

### Vulnerability 4

#### A07:2021 – Identification and Authentication Failures

Here we can see that the vulnerability is that the page does not have any requirements for a users password. This is a major risk for brute force attacks since attackers can easily try out the most common / simple passwords like "1".

The fix has requirements that the password must be at least 8 characters, contain at least one of each: uppercase letter, number and special character. This makes it more difficult for attackers to get access to users accounts.

Below are the fixes:

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L63-72
https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/app.py#L83-85


### Vulnerability 5

#### A03:2021 – Injection

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/templates/dashboard.html#L18

The vulnerability here is Cross-site Scripting (XSS). This is done by using the `| safe` filter in the Jinja2 template. This way, the application is instructed to trust user input and render the note's content as raw HTML. This is a major vulnerability since it allows attackers to inject JavaScript code into the application.

The fix is to remove the "safe" part of the filter. By doing that Flask's Jinja2 template automatically escapes HTML and the malicious script is not executed but instead shown as plain text in the note.

https://github.com/filippahognasbacka/Cyber-Security-Base-project/blob/main/templates/dashboard.html#L21

