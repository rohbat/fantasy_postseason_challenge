from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from flask_login import login_user, login_required, logout_user, current_user

from .account import User

from bson.objectid import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route("/logged_in")
@login_required
def logged_in():
    # print("Handling request to logged in home page.")
    print(current_user.username)
    return render_template("logged_in.html")
