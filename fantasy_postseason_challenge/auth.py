from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# from flask import current_app as app
from flask_login import login_user, login_required, logout_user, current_user

from .account import User

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route("/")
def hello():
    return render_template("home.html")

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        e = None
        if not (username and password):
            e = "username and password required"
        elif User.objects(username=username).first():
            e = f"Username: \"{username}\" already exists"
        
        if not e:
            new_user = User(username=username, password_hash=generate_password_hash(password))
            new_user.save()
            return redirect(url_for("auth.login"))
        else:
            flash(e)

    return render_template("register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.objects(username=username).first()
        
        e = None
        if not (username and password):
            e = "username and password required"
        elif not user:
            e = f"Username: \"{username}\" not found"
        elif not check_password_hash(user.password_hash, password):
            e = "Incorrect password"

        if not e:
            # session.clear()
            login_user(user)
            return redirect(url_for("dashboard.logged_in"))
        else:
            flash(e)
    
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("auth.hello"))

# this is bad now right?
'''
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
'''