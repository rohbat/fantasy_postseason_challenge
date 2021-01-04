from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_user, login_required, logout_user, current_user

from .account import User
from .league import League, Member
from .fantasy_team import FantasyTeam, Player
from .forms import SelectTeamForm

from bson.objectid import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    league_memberships = current_user.memberships
    print(league_memberships)
    return render_template("logged_in_homepage.html", league_memberships=league_memberships)

@bp.route("/select_team/<league_id>", methods=("GET", "POST"))
@login_required
def select_team(league_id):
    # TODO: detect preexisting teams within a league
    form = SelectTeamForm(request.form)
    if request.method == "POST":
        if form.validate_week_1():

            fantasy_team = FantasyTeam(
                QB = form.data["QB"],
                RB1 = form.data["RB1"],
                RB2 = form.data["RB2"],
                WR1 = form.data["WR1"],
                WR2 = form.data["WR2"],
                TE = form.data["TE"],
                FLEX = form.data["FLEX"],
                K = form.data["K"],
                D_ST = form.data["D_ST"]
            )
            fantasy_team.save()

            league = League.objects(id=league_id).first()
            for member in league.member_id_list:
                member_id = member.account_id
                if member_id == current_user.id:
                    member.week_1_team = fantasy_team
            league.save()

            # TODO: figure out how to delete the team that's being replaced if
            #       one already exists

            return redirect(url_for("dashboard.view_league", league_id=league_id))

        else:
            e = "Invalid team composition"
            flash(e)

    qbs = Player.objects(position="QB", week_1_avail=True)
    rbs = Player.objects(position="RB", week_1_avail=True)
    wrs = Player.objects(position="WR", week_1_avail=True)
    tes = Player.objects(position="TE", week_1_avail=True)
    ks = Player.objects(position="K", week_1_avail=True)
    d_sts = Player.objects(position="D/ST", week_1_avail=True)

    form.QB.choices = [(qb.id, qb.display_name) for qb in qbs]
    form.RB1.choices = form.RB2.choices = [(rb.id, rb.display_name) for rb in rbs]
    form.WR1.choices = form.WR2.choices = [(wr.id, wr.display_name) for wr in wrs]
    form.TE.choices = [(te.id, te.display_name) for te in tes]
    form.FLEX.choices = form.RB1.choices + form.WR1.choices + form.TE.choices
    form.K.choices = [(k.id, k.display_name) for k in ks]
    form.D_ST.choices = [(d_st.id, d_st.display_name) for d_st in d_sts]
    return render_template("select_team.html", form=form)


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
        league_id=league_id,
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

            # Create new member object and save to db
            new_member = Member(team_name=team_name, 
                                account_id=current_user.id)

            # Create new league object and save to db
            new_league = League(league_name=league_name, 
                                ruleset=ruleset, 
                                commissioner_id=current_user.id,
                                member_id_list=[new_member])

            new_league.save()

            # Append new member id to new league's member list
            # new_league.update(push__member_id_list=new_member)

            # Append new league id to current user's league membership list
            current_user.update(push__memberships=new_league)

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
                                account_id=current_user.id)
            new_member.save()

            # Append new member id to new league's member list
            league.update(push__member_id_list=new_member)

            # Append new league id to current user's league membership list
            current_user.update(push__memberships=league)

            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("join_league.html")