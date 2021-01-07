from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_user, login_required, logout_user, current_user

from .account import Account

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route("/")
def welcome():
    return render_template("welcome.html")

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        display_name = request.form["display_name"]

        e = None
        if not (username and password and display_name):
            e = "username, password and display name required"
        elif Account.objects(username=username).first():
            e = f"Username: \"{username}\" already exists"
        
        if not e:
            new_user = Account(username=username, password_hash=generate_password_hash(password), display_name=display_name)
            new_user.save()
            login_user(new_user)
            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)

    return render_template("register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        e = None
        if not (username and password):
            e = "username and password required"
        
        user = Account.objects(username=username).first()

        if not user:
            e = f"Username: \"{username}\" not found"
        elif not check_password_hash(user.password_hash, password):
            e = "Incorrect password"

        if not e:
            # session.clear()
            login_user(user)
            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")

    return redirect(url_for("auth.welcome"))