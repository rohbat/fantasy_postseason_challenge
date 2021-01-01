from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from flask_login import login_user, login_required, logout_user, current_user

from .account import User
from .league import League

from bson.objectid import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    print(current_user.id)
    membership_ids = current_user.memberships
    return render_template("logged_in_homepage.html")

@bp.route("/new_league", methods=("GET", "POST"))
@login_required
def new_league():
    if request.method == "POST":
        league_name = request.form["league_name"]
        ruleset = request.form["ruleset"]
        team_name = request.form["team_name"]
        
        e = None
        if not (league_name and ruleset):
            e = "league name and ruleset required"

        if not e:
            new_league = League(league_name=league_name, ruleset=ruleset)
            new_league.commissioner_id = current_user.id
            new_league.member_id_list = ['test']
            new_league.save()

            # TODO: Create Member class and table, update account and league with membership-id 
            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("new_league.html")

@bp.route("/join_league", methods=("GET", "POST"))
@login_required
def join_league():
    membership_ids = current_user.memberships
    return render_template("logged_in_homepage.html")