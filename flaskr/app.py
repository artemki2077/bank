from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import json

# dbconfig = {
#     'host': 'localhost',
#     'user': 'postgres',
#     'port': '5432',
#     'password': 'postgres',
#     'database': 'bank',
# }

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/bank'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    def __init__(self, login=None, password=None, account_id=None):
        self.login = login
        self.password = password
        self.account_id = account_id

    def __repr__(self):
        # return '%r' % self.account_id
        return f'User(login={self.login}, id={self.account_id})'


class Projects(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, login=None, password=None, account_id=None, user_id=user_id):
        self.login = login
        self.password = password
        self.account_id = account_id
        self.user_id = user_id

    def __repr__(self):
        return f'Project(login={self.login}, accid={self.account_id}, user_id={self.user_id})'


class Accounts(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, nullable=False)

    def __init__(self, balance=None):
        self.balance = balance

    def __repr__(self):
        return f'Account(id={self.id},balance={self.balance})'


class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    account_id_from = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, )
    account_id_to = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, account_id_from=None, account_id_to=None, amount=None, comment=None):
        self.account_id_from = account_id_from
        self.account_id_to = account_id_to
        self.amount = amount
        self.comment = comment

    def __repr__(self):
        return f'Transaction(id={self.id},account_id_from={self.account_id_from},' \
               f'account_id_to={self.account_id_to},amount={self.amount},comment' \
               f'={self.comment},time={self.time})'


# conn = psycopg2.co = nnect(**dbconfig)
# cur = conn.cursor()


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ""
    if request.method == 'POST':
        messages = json.dumps({"id": str(request.form.get('username'))})
        user = valid_login(str(request.form.get('username')), str(request.form.get('password')))
        if user:
            session["username"] = request.form.get("username")
            session["account_id"] = user.account_id
            return redirect(url_for("user", id=session["username"]))
        else:
            project = valid_project_login(str(request.form.get('username')),
                                          str(request.form.get('password')))
            if project:
                session["project_name"] = request.form.get("username")
                session["account_id"] = project.account_id
                return redirect(url_for("project", _id=session["project_name"]))
            else:
                error = 'Invalid username/password'
    return render_template('index.html', error=error)


def valid_project_login(login, password):
    project = Projects.query.filter_by(login=login, password=password).first()
    return project


@app.route("/api", methods=['POST', 'GET'])
def api():
    error = ''
    if request.method == 'GET':
        ac_id = okpolzvl(request.args.get('from'), request.args.get('password'))
        if ac_id:
            if valid_user_api(request.args.get('to')):
                if check_balance_api(request.args.get('amount'), ac_id):
                    spisanie(ac_id, request.args.get('amount'))
                    nachislenie(request.args.get('to'), request.args.get('amount'))
                    savetran(ac_id, request.args.get('to'), request.args.get('amount'), request.args.get('comment'))
                    error = 'success'
                else:
                    error = "You don't have enough money"
            else:
                error = "User doesn't exist"
        else:
            error = "password/login error"
    return jsonify({"answer": error})


def check_balance_api(amount, nn):
    a = Accounts.query.filter_by(id=nn).first()
    if str(amount).isnumeric():
        return a.balance >= int(amount)


def okpolzvl(login, password):
    a = Users.query.filter_by(login=login, password=password).first()
    db.session.commit()
    if a is not None:
        return a.account_id


def valid_login(login, password):
    user = Users.query.filter_by(login=login, password=password).first()
    db.session.commit()
    return user


def valid_user_api(login):
    user = Projects.query.filter_by(login=login).first()
    db.session.commit()
    return user


@app.route("/users/<id>", methods=['POST', 'GET'])
def user(id):
    if session.get("username") is None or session.get("username") != id:
        redirect("/")
    error = ''
    if request.method == 'POST':
        if session.get("username") is not None or session.get("project_name") is not None:
            if valid_user(request.form.get('to')):
                if check_balance(request.form.get('amount')):
                    spisanie(session.get('account_id'), request.form.get('amount'))
                    nachislenie(request.form.get('to'), request.form.get('amount'))
                    savetran(session.get('account_id'), request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
                    print(request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
                    return redirect("/")
                else:
                    error = "You don't have enough money"
            else:
                error = "User doesn't exist"
        else:
            error = "You don't log in"
    print(error)
    # select = f"select balance from accounts where account_id = {session.get('account_id')}"
    # cur.execute(select)
    # money = cur.fetchall()[0][0]
    account = Accounts.query.filter_by(id=session.get('account_id')).first()
    # select = f"select account_id_from, account_id_to, amount, comment_ " \
    #          f"from transactions where " \
    #          f"account_id_to = '{session.get('account_id')}' or " \
    #          f"account_id_from = '{session.get('account_id')}'"
    # cur.execute(select)
    # transactions = cur.fetchall()
    transactions = Transactions.query.filter_by(
        account_id_to=session.get('account_id')).all() + Transactions.query.filter_by(
        account_id_from=session.get('account_id')).all()
    users = Users.query.all()
    projects = Projects.query.all()
    accounts = {}
    for i in users + projects:
        accounts[i.account_id] = i.login
    if not session.get("username"):
        return redirect("/login")
    return render_template('user.html', name=session.get("username"), money=account.balance,
                           transactions=transactions, ids=accounts, error=error)


@app.route("/project/<_id>", methods=['POST', 'GET'])
def project(_id):
    if not session.get("project_name") or session.get("project_name") != _id:
        return redirect("/")

    error = ''
    if request.method == 'POST':
        if session.get("username") is not None or session.get("project_name") is not None:
            if valid_user(request.form.get('to')):
                if check_balance(request.form.get('amount')):
                    spisanie(session.get('account_id'), request.form.get('amount'))
                    nachislenie(request.form.get('to'), request.form.get('amount'))
                    savetran(session.get('account_id'), request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
                    print(request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
                    return redirect("/")
                else:
                    error = "You don't have enough money"
            else:
                error = "User doesn't exist"
        else:
            error = "You don't log in"
    print(error)
    # select = f"select balance from accounts where account_id = {session.get('account_id')}"
    # cur.execute(select)
    # money = cur.fetchall()[0][0]
    account = Accounts.query.filter_by(id=session.get('account_id')).first()
    # select = f"select account_id_from, account_id_to, amount, comment_ " \
    #          f"from transactions where " \
    #          f"account_id_to = '{session.get('account_id')}' or " \
    #          f"account_id_from = '{session.get('account_id')}'"
    # cur.execute(select)
    # transactions = cur.fetchall()
    transactions = Transactions.query.filter_by(
        account_id_to=session.get('account_id')).all() + Transactions.query.filter_by(
        account_id_from=session.get('account_id')).all()
    users = Users.query.all()
    projects = Projects.query.all()
    accounts = {}
    for i in users + projects:
        accounts[i.account_id] = i.login
    return render_template('user.html', name=_id, money=account.balance, transactions=transactions,
                           ids=accounts)


@app.route("/ProjectToUser", methods=['POST', 'GET'])
def add_project_to_user():
    error = ""
    if request.method == 'POST':
        users = Users.query.filter_by(login=str(request.form.get('username')), password=str(request.form.get('password'))).all()
        if users:
            u_id = users[0].id
            me = Accounts(0)
            db.session.add(me)
            db.session.commit()
            a_id = me.id
            if not user:
                error = "problem with login or password"
            else:
                me = Projects(login=session["pr_login"], password=session['pr_password'], account_id=a_id, user_id=u_id)
                db.session.add(me)
                db.session.commit()
                return redirect("/login")
        else:
            error = "not such user"
    return render_template('project_to_user.html', error=error)


@app.route("/logout")
def logout():
    session["username"] = None
    session["project_id"] = None
    return redirect("/login")


def save(login, password, check="off"):
    if len(login) < 2 or len(login) < 2:
        return "The password or login is shorter than 2 characters"
    users = Users.query.filter_by(login=login).all()
    print(users)
    if users:
        return "this username is already in use"

    projects = Projects.query.filter_by(login=login).all()

    if projects:
        return "this project name is already in use"
    account = Accounts.query.order_by(Accounts.id.desc()).all()
    print(account)
    _id = account[0].id + 1
    # me = Accounts(1000 * (check == "on"))
    # db.session.add(me)
    # db.session.commit()
    # save = "INSERT INTO accounts(balance) VALUES (1000)"
    # cur.execute(save)
    # conn.commit()
    # accid = "SELECT max(account_id) FROM accounts "
    # cur.execute(accid)
    # id = ''
    if check == 'on':
        session["pr_login"] = login
        session['pr_password'] = password
        return "proj"
        # insert = "INSERT INTO projects (project_login, project_password,account_id) VALUES
        # '('" + login + "', '" + password + "', " + str(
        #     id) + ");"
    else:
        me = Accounts(0 if check == "on" else 1000)
        db.session.add(me)
        db.session.commit()
        session["account_id"] = _id
        me = Users(login=login, password=password, account_id=_id)
        # insert = "INSERT INTO users (user_login, user_password,account_id) VALUES
        # ('" + login + "', '" + password + "', " + str(
        # id) + ")"                                                                                                                                                  ";"
    db.session.add(me)
    db.session.commit()
    return ''


@app.route("/singup", methods=['POST', 'GET'])
def singUp():
    error = ""
    if request.method == 'POST':
        ee = save(str(request.form.get('username')), str(request.form.get('password')),
                  str(request.form.get('onoffswitch')))
        if not ee:
            return redirect("/login")
        elif ee != "proj":
            error = ee
        else:
            return redirect("/ProjectToUser")
    return render_template('singup.html', error=error)


# @app.route('transaction', methods=['POST', 'GET'])
# def money():
#     error = ''
#     if request.method == 'POST':
#         if session.get("username") is not None or session.get("project_name") is not None:
#             if valid_user(request.form.get('to')):
#                 if check_balance(request.form.get('amount')):
#                     spisanie(session.get('account_id'), request.form.get('amount'))
#                     nachislenie(request.form.get('to'), request.form.get('amount'))
#                     savetran(session.get('account_id'), request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
#                     print(request.form.get('to'), request.form.get('amount'), request.form.get('comment'))
#                     return redirect("/")
#                 else:
#                     error = "You don't have enough money"
#             else:
#                 error = "User doesn't exist"
#         else:
#             error = "You don't log in"
#     return render_template('transactions.html', error=error)


def is_it_project(name):
    return Projects.query.filter_by(login=name).first()


def check_balance(amount):
    a = Accounts.query.filter_by(id=session.get('account_id')).first()
    print(a, amount)
    if str(amount).isnumeric():
        return a.balance >= int(amount)

    # select = "SELECT balance FROM accounts WHERE account_id="+session.get('id')+""
    # cur.execute(select)
    # balance = 0
    # for row in cur.fetchall():
    #     balance = int(row[0])
    # if int(amount) > balance:
    #     return False
    # else:
    #     return True


def valid_user(name):
    p = Projects.query.filter_by(login=name).all()
    u = Users.query.filter_by(login=name).all()
    return p + u


def spisanie(id, amount):
    a = Accounts.query.filter_by(id=id).first()
    a.balance -= int(amount)
    db.session.commit()
    # select = "SELECT balance FROM accounts WHERE account_id="+id+""
    # cur.execute(select)
    # balance = 0
    # for row in cur.fetchall():
    #     balance = int(row[0])
    # balance -= int(amount)
    # update = "UPDATE accounts SET balance="+str(balance)+"WHERE account_id="+id
    # cur.execute(update)
    # conn.commit()


def nachislenie(name, amount):
    if is_it_project(name):
        p = Projects.query.filter_by(login=name).first()
        _id = p.account_id
    else:
        p = Users.query.filter_by(login=name).first()
        _id = p.account_id
    a = Accounts.query.filter_by(id=_id).first()
    a.balance += int(amount)
    db.session.commit()
    # if is_it_project(name):
    #     select = "SELECT account_id FROM projects WHERE project_login='"+name+"'"
    # else:
    #     select = "SELECT account_id FROM users WHERE user_login='"+name+"'"
    # cur.execute(select)
    # id = ''
    # for row in cur.fetchall():
    #     id = str(row[0])
    # select = "SELECT balance FROM accounts WHERE account_id=" + id + ""
    # cur.execute(select)
    # balance = 0
    # for row in cur.fetchall():
    #     balance = int(row[0])
    # balance += int(amount)
    # update = "UPDATE accounts SET balance=" + str(balance) + "WHERE account_id=" + id
    # cur.execute(update)
    # conn.commit()


def savetran(idfrom, name, amount, comment):
    if is_it_project(name):
        p = Projects.query.filter_by(login=name).first()
    else:
        p = Users.query.filter_by(login=name).first()
    id_to = p.account_id
    me = Transactions(account_id_from=idfrom, account_id_to=id_to, amount=int(amount), comment=comment)
    db.session.add(me)
    db.session.commit()
    # if is_it_project(name):
    #     select = "SELECT account_id FROM projects WHERE project_login='"+name+"'"
    # else:
    #     select = "SELECT account_id FROM users WHERE user_login='"+name+"'"
    # cur.execute(select)
    # idto = ''
    # for row in cur.fetchall():
    #     idto = str(row[0])
    # insert = "INSERT INTO transactions(account_id_from,account_id_to,amount,comment_) VALUES ("+idfrom+", "+idto+", "+amount+", '"+str(comment)+"')"
    # cur.execute(insert)
    # conn.commit()


@app.route("/")
def f():
    if not session.get("username"):
        return redirect("/login")
    return redirect(url_for("user", id=session["username"]))


if __name__ == "__main__":
    app.run(debug=False, port=8000, host="0.0.0.0")
db.create_all()