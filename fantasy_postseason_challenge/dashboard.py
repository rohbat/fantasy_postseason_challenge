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

@bp.route("/league/<league_id>")
@login_required
def view_league(league_id):
    print(current_user.username)
    print(league_id)

    # making some assumptions about league structure
    # hardcoding data until figure out table structures
    # TODO: figure this out and fix
    data = {
        "b": {"pos1": "wolf1", "pos2": "tiger2", "pos3": "fox3"},
        "joe": {"pos1": "wolf1", "pos2": "wolf2", "pos3": "fox3"},
        "c": {"pos1": "fox1", "pos2": "fox2", "pos3": "fox3"},
    }

    player_membership = {
        "wolf1" : "wolf",
        "wolf2" : "wolf",
        "wolf3" : "wolf",
        "tiger1" : "tiger",
        "tiger2" : "tiger",
        "tiger3" : "tiger",
        "fox1" : "fox",
        "fox2" : "fox",
        "fox3" : "fox",
    }
    player_scores = {
        "wolf1" : 9,
        "wolf2" : 8,
        "wolf3" : 123,
        "tiger1" : 2,
        "tiger2" : 2,
        "tiger3" : 28,
        "fox1" : -17,
        "fox2" : 17,
        "fox3" : 107,
    }
    team_colors = {
        "wolf": ("#808080", "#FF00FF"),
        "tiger": ("#FF9900", "#000000"),
        "fox": ("#FF0000", "#FFFFFF"),
    }
    positions = ["pos1", "pos2", "pos3"]

    members = sorted(data, key=lambda x: x == current_user.username, reverse=True)
    table = [[data[member][position] for member in members] for position in positions]
    table = [
        [
            (player, player_scores[player], *team_colors[player_membership[player]])
            for player in row
        ]
        for row in table
    ]

    return render_template(
        "view_league.html",
        positions=positions,
        members=members,
        data=table,
        score_width=50, # TODO: choose good values for these and put in html?
        name_width=150, # TODO: choose good values for these and put in html?
        zip=zip,
        enumerate=enumerate,
        len=len
    )

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
            # TODO: Make insert operations such that there's no issues if a middle operation fails

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

            # Append new member id to current user's league membership list
            current_user.update(push__memberships=new_member.id)

            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("new_league.html")

@bp.route("/join_league", methods=("GET", "POST"))
@login_required
def join_league():
    if request.method == "POST":
        league_id = request.form["league_id"]
        team_name = request.form["team_name"]
        
        e = None
        if not (league_id and team_name):
            e = "league id and team name required"
        
        try:
            league = League.objects(id=ObjectId(league_id)).first()
        except:
            e = f"League with ID: \"{league_id}\" not found"
        
        #TODO: Check if current user is already in this league.

        if not e:
            # TODO: Make insert operations such that there's no issues if a middle operation fails

            # Create new member object and save to db
            new_member = Member(team_name=team_name, 
                                account_id=current_user.id, 
                                league_name=league.league_name, 
                                league_id=league.id)
            new_member.save()

            # Append new member id to new league's member list
            league.update(push__member_id_list=new_member.id)

            # Append new member id to current user's league membership list
            current_user.update(push__memberships=new_member.id)

            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("join_league.html")