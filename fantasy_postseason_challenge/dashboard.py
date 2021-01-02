from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from flask_login import login_user, login_required, logout_user, current_user

from .account import User
from .league import League
from .member import Member

from bson.objectid import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    print(current_user.id)
    membership_ids = current_user.memberships
    members = Member.objects(id__in=membership_ids)
    print(members)
    return render_template("logged_in_homepage.html", members=members)

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
            # TODO: Make insert operations cascade such that there's no issues if a middle operation fails

            # Create new league object and save to db
            new_league = League(league_name=league_name, 
                                ruleset=ruleset, 
                                commissioner_id=current_user.id,
                                member_id_list=[])
            new_league.save()

            # Create new member object and save to db
            new_member = Member(team_name=team_name, 
                                account_id=current_user.id, 
                                league_name=league_name, 
                                league_id=new_league.id)
            new_member.save()

            # Append new member id to new league's member list
            new_league.update(push__member_id_list=new_member.id)
            new_league.save()

            # Append new member id to current user's league membership list
            current_user.update(push__memberships=new_member.id)
            current_user.save()

            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("new_league.html")

@bp.route("/join_league", methods=("GET", "POST"))
@login_required
def join_league():
    membership_ids = current_user.memberships
    return render_template("logged_in_homepage.html")