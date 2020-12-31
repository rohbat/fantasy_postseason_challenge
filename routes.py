from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash

mongo = PyMongo(app)

@app.route("/")
def hello():
    print("Handling request to home page.")
    return "I'm gonna be a football app."

@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        accounts = mongo.db.test_accounts

        e = None
        if not (username and password):
            e = "username and password required"
        elif accounts.find_one({"username" : username}):
            e = f"{username} already exists"
        
        if not e:
            new_user = {'username' : username, 'password_hash' : generate_password_hash(password)}
            post_id = accounts.insert_one(new_user).inserted_id
            return redirect(url_for("login"))
        else:
            flash(e)

    return render_template("register.html")

@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        accounts = mongo.db.test_accounts
        account = accounts.find_one({"username" : username})
        
        e = None
        if not (username and password):
            e = "username and password required"
        elif not account:
            e = f"{username} does not exist"
        elif not check_password_hash(account["password_hash"], password):
            e = "incorrect password"

        if not e:
            session.clear()
            session["user_id"] = str(account["_id"])
            flash(str(account["_id"]))
            time.sleep(10)
            return redirect(url_for("hello"))
        else:
            flash(e)

@app.route("/check_user_id")
def check_user_id():
    accounts = mongo.db.test_accounts

    if "user_id" in session:
        account = accounts.find_one({"_id" : ObjectId(session["user_id"])})
        
        if not account:
            return "No account" + session["user_id"]
        else:
            return account['username']
    else:
        return "No session"
