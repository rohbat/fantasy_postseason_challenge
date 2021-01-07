from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_user, login_required, logout_user, current_user

from .account import Account
from .league import League, Member
from .fantasy_team import FantasyTeam, Player
from .forms import SelectTeamForm

from bson.objectid import ObjectId

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    league_memberships = current_user.memberships
    team_names = []
    league_commissionerships = []

    for league_membership in league_memberships:
        for member in league_membership.member_list:
            if member.account_id == current_user.id:
                team_names.append(member.team_name)
                break
        if league_membership.commissioner_id == current_user.id:
            league_commissionerships.append(league_membership)

    return render_template(
        "logged_in_homepage.html",
        league_memberships=league_memberships,
        team_names=team_names,
        league_commissionerships=league_commissionerships,
        zip=zip,
    )

@bp.route("/select_team/<league_id>", methods=("GET", "POST"))
@login_required
def select_team(league_id):
    form = SelectTeamForm(request.form)
    if request.method == "POST":
        if form.validate_week_1():
            #TODO: Update instead of create new object when team already exists.
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

            league = try_get_league_by_id(league_id)
            for member in league.member_list:
                if member.account_id == current_user.id:
                    member.week_1_team = fantasy_team
            league.save()

            return redirect(url_for("dashboard.view_league", league_id=league_id))

        else:
            e = "Invalid team composition"
            flash(e)

    qbs = sorted(Player.objects(position="QB", week_1_avail=True), key=lambda x: x.games_started, reverse=True)
    rbs = sorted(Player.objects(position="RB", week_1_avail=True), key=lambda x: x.games_started, reverse=True)
    wrs = sorted(Player.objects(position="WR", week_1_avail=True), key=lambda x: x.games_started, reverse=True)
    tes = sorted(Player.objects(position="TE", week_1_avail=True), key=lambda x: x.games_started, reverse=True)
    ks = sorted(Player.objects(position="K", week_1_avail=True), key=lambda x: x.games_started, reverse=True)
    d_sts = sorted(Player.objects(position="D/ST", week_1_avail=True), key=lambda x: x.games_started, reverse=True)

    form.QB.choices = [(qb.id, qb.display_name) for qb in qbs]
    form.RB1.choices = form.RB2.choices = [(rb.id, rb.display_name) for rb in rbs]
    form.WR1.choices = form.WR2.choices = [(wr.id, wr.display_name) for wr in wrs]
    form.TE.choices = [(te.id, te.display_name) for te in tes]
    form.FLEX.choices = [(flex.id, flex.display_name) for flex in sorted(rbs + wrs + tes, key=lambda x: x.games_started, reverse=True)]
    form.K.choices = [(k.id, k.display_name) for k in ks]
    form.D_ST.choices = [(d_st.id, d_st.display_name) for d_st in d_sts]

    return render_template("select_team.html", form=form)


@bp.route("/league/<league_id>")
@login_required
def view_league(league_id):
    league = try_get_league_by_id(league_id)

    league_members = league.member_list
    league_members = sorted(league_members, key=lambda x: x.account_id == current_user.id, reverse=True)

    team_names = [member.team_name for member in league_members]
    member_names = [Account.objects(id=member.account_id).first().display_name for member in league_members]
    league_teams = [member.week_1_team for member in league_members]
    print(team_names)
    print(league_teams)

    positions = ["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "D/ST"]
    ['KC', 'BUF', 'PIT', 'TEN', 'BAL', 'CLE', 'IND', 'GB', 'NO', 'SEA', 'WAS', 'TB', 'LAR', 'CHI']
    team_colors = {
        'None' : ("#808080", "#FF00FF"),
        'KC' : ("#E31837", "#FFB81C"),
        'BUF' : ("#C60C30", "#00338D"),
        'PIT' : ("#101820", "#FFB612"),
        'TEN' : ("#4B92DB", "#0C2340"),
        'BAL' : ("#241773", "#FFFFFF"),
        'CLE' : ("#311D00", "#FF3C00"),
        'IND' : ("#002C5F", "#FFFFFF"),
        'GB' : ("#203731", "#FFB612"),
        'NO' : ("#D3BC8D", "#101820"),
        'SEA' : ("#002244", "#69BE28"),
        'WAS' : ("#773141", "#FFB612"),
        'TB' : ("#D50A0A", "#0A0A08"),
        'LAR' : ("#003594", "#FFD100"),
        'CHI' : ("#0B162A", "#C83803"),
    }

    #TODO: Refactor this.
    data = []

    if league_teams:
        data.append([(team.QB.display_name, 0, *team_colors[team.QB.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.RB1.display_name, 0, *team_colors[team.RB1.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.RB2.display_name, 0, *team_colors[team.RB2.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.WR1.display_name, 0, *team_colors[team.WR1.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.WR2.display_name, 0, *team_colors[team.WR2.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.TE.display_name, 0, *team_colors[team.TE.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.FLEX.display_name, 0, *team_colors[team.FLEX.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.K.display_name, 0, *team_colors[team.K.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])
        data.append([(team.D_ST.display_name, 0, *team_colors[team.D_ST.team]) if team else ('set ur lineup', 0, *team_colors['None']) for team in league_teams])

    return render_template(
        "view_league.html",
        positions=positions,
        team_names=team_names,
        member_names=member_names,
        data=data,
        league=league,
        position_width=60,
        score_width=50, # TODO: choose good values for these and put in html?
        name_width=180, # TODO: choose good values for these and put in html?
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
                                member_list=[new_member])

            new_league.save()

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
        
        league = try_get_league_by_id(league_id)
        
        #TODO: Check if current user is already in this league.

        if not e:
            # TODO: Make insert operations such that there's no issues if a middle operation fails

            # Create new member object and save to db
            new_member = Member(team_name=team_name, 
                                account_id=current_user.id)

            # Append new member id to new league's member list
            league.update(push__member_list=new_member)

            # Append new league id to current user's league membership list
            current_user.update(push__memberships=league)

            return redirect(url_for("dashboard.logged_in_homepage"))
        else:
            flash(e)
    
    return render_template("join_league.html")

def try_get_league_by_id(league_id):
    try:
        league = League.objects(id=ObjectId(league_id)).first()
        return league
    except:
        e = f"League with ID: \"{league_id}\" not found"