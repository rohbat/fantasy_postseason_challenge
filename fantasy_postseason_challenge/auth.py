from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, logout_user, current_user
from .auth_service import register_user, authenticate_user
from .forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route("/")
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.logged_in_homepage"))
    else:
        return render_template("welcome.html")

@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        display_name = form.display_name.data

        success, message = register_user(username, password, display_name)
        flash(message)
        if success:
            return redirect(url_for("dashboard.logged_in_homepage"))
        
    return render_template("register.html", form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user, message = authenticate_user(username, password)
        flash(message)
        print(user)
        if user:
            return redirect(url_for("dashboard.logged_in_homepage"))
    
    return render_template("login.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")

    return redirect(url_for("auth.welcome"))