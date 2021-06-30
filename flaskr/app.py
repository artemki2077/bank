from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import json
import psycopg2

dbconfig = {
    'host': 'localhost',
    'user': 'postgres',
    'port': '5432',
    'password': 'postgres',
    'database': 'bank',
}

conn = psycopg2.connect(**dbconfig)
cur = conn.cursor()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ""
    if request.method == 'POST':
        messages = json.dumps({"id": str(request.form.get('username'))})
        if valid_login(str(request.form.get('username')), str(request.form.get('password'))):
            session["username"] = request.form.get("username")
            select = f"SELECT account_id FROM users where user_login = '{request.form.get('username')}'"
            cur.execute(select)
            session["account_id"] = cur.fetchall()[0][0]
            return redirect(url_for("user", id=session["username"]))
        else:
            if valid_project_login(str(request.form.get('username')),
                                   str(request.form.get('password'))):
                session["project_name"] = request.form.get("username")
                select = f"SELECT account_id FROM projects where project_login = '{request.form.get('username')}'"
                cur.execute(select)
                h = cur.fetchall()
                session["account_id"] = h[0][0]
                return redirect(url_for("project", id=session["project_name"]))
            else:
                error = 'Invalid username/password'
    return render_template('index.html', error=error)


def valid_project_login(login, password):
    select = "SELECT project_login, project_password FROM projects where project_" \
             "login='" + login + "' and project_password = '" + password + "'"
    cur.execute(select)
    answ = cur.fetchall()
    return answ


def valid_login(login, password):
    select = "SELECT user_login,user_password FROM users where user_l" \
             "ogin='" + login + "' and user_password = '" + password + "'"
    cur.execute(select)
    answ = cur.fetchall()
    return answ


@app.route("/users/<id>", methods=['POST', 'GET'])
def user(id):
    select = f"select balance from accounts where account_id = {session.get('account_id')}"
    cur.execute(select)
    money = cur.fetchall()[0][0]
    select = f"select * from transactions where account_id_to = '{session.get('account_id')}' or a" \
             f"ccount_id_from = '{session.get('account_id')}'"
    cur.execute(select)
    transactions = cur.fetchall()
    if not session.get("username"):
        return redirect("/login")
    return render_template('user.html', name=id, money=money, transactions=transactions)


def all_id(h):
    select = f"select user_login, account_id from users"
    cur.execute(select)
    users = {}
    for i in cur.fetchall():
        users[i[1]] = i[0]
    select = f"select project_login, account_id from projects"
    cur.execute(select)
    for i in cur.fetchall():
        users[i[1]] = i[0]
    all = {}
    for i in h:
        if i in users:
            all[i] = users[i]
    return all


@app.route("/project/<id>", methods=['POST', 'GET'])
def project(id):
    select = f"select balance from accounts where account_id = {session.get('account_id')}"
    cur.execute(select)
    money = cur.fetchall()[0][0]
    select = f"select account_id_from, account_id_to, amount, comment_ " \
             f"from transactions where " \
             f"account_id_to = '{session.get('account_id')}' or " \
             f"account_id_from = '{session.get('account_id')}'"
    cur.execute(select)
    transactions = cur.fetchall()
    h = []
    for i in transactions:
        h.extend([i[0], i[1]])

    d = all_id(set(h))
    print(set(h))
    print(d)
    if not session.get("project_name"):
        return redirect("/login")
    return render_template('user.html', name=id, money=money, transactions=transactions, ids=d)


@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/login")


def save(login, password, check="off"):
    if len(login) < 2 or len(login) < 2:
        return "The password or login is shorter than 2 characters"
    select = f"select * from users;"
    cur.execute(select)

    for i in cur.fetchall():
        if i[1] == login:
            return "this username is already in use"
    conn.commit()
    select = f"select * from projects;"
    cur.execute(select)

    for i in cur.fetchall():
        if i[1] == login:
            return "this project name is already in use"

    conn.commit()
    save = "INSERT INTO accounts(balance) VALUES (1000)"
    cur.execute(save)
    conn.commit()
    accid = "SELECT max(account_id) FROM accounts "
    cur.execute(accid)
    id = ''
    for row in cur.fetchall():
        id = row[0]
    session["accid"] = str(id)
    if check == 'on':
        insert = "INSERT INTO projects (project_login, project_password,account_id) VALUES ('" + login + "', '" + password + "', " + str(
            id) + ");"
    else:
        insert = "INSERT INTO users (user_login, user_password,account_id) VALUES ('" + login + "', '" + password + "', " + str(
            id) + ")"                                                                                                                                                  ";"
    cur.execute(insert)
    conn.commit()
    return ''


@app.route("/singup", methods=['POST', 'GET'])
def singUp():
    error = ""
    if request.method == 'POST':
        ee = save(str(request.form.get('username')), str(request.form.get('password')),
                  str(request.form.get('onoffswitch')))
        if not ee:
            return redirect("/login")
        else:
            error = ee
    return render_template('singup.html', error=error)


@app.route("/")
def f():
    if not session.get("username"):
        return redirect("/login")
    return redirect(url_for("user", id=session["username"]))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
