from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from flask_login import login_user, login_required, logout_user, current_user

from .classes.user import User
from .classes.league import League, Member
from .classes.lineup import Lineup
from .classes.player import Player
from .forms import SelectTeamForm
from .utilities import is_round_locked
from .db import db
from bson.dbref import DBRef

from bson.objectid import ObjectId

from datetime import datetime
from dateutil import tz
from decimal import Decimal

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    # Dereference league memberships
    league_memberships = [League.objects(id=league.id).first() for league in current_user.memberships]
    league_commissionerships = []

    # Find team names for each league
    team_names = []
    for league in league_memberships:
        for member in league.member_list:
            team_names.append(member.team_name)

    # Find all leagues where the current user is the commissioner
    if league_memberships:
        league_commissionerships = League.objects(commissioner=current_user.id)

    return render_template(
        "logged_in_homepage.html",
        league_memberships=league_memberships,
        team_names=team_names,
        league_commissionerships=league_commissionerships,
    )

@bp.route("/select_team/<league_id>", methods=("GET", "POST"))
@login_required
def select_team(league_id):
    current_round = 'divisional'  # Determine the current round programmatically or from user input

    if is_round_locked(current_round):
        flash("Picks have locked for the wildcard round")
        return redirect(url_for("dashboard.view_league", league_id=league_id))

    week = current_app.CURRENT_ROUND

    form = SelectTeamForm(request.form)
    if request.method == "POST":
        player_ids = {
            "QB": form.data["QB"],
            "RB1": form.data["RB1"],
            "RB2": form.data["RB2"],
            "WR1": form.data["WR1"],
            "WR2": form.data["WR2"],
            "TE": form.data["TE"],
            "FLEX": form.data["FLEX"],
            "K": form.data["K"],
            "D_ST": form.data["D_ST"]
        }

        teams = []
        for player_id in player_ids.values():
            if player_id:
                player = Player.objects(id=player_id).first()
                if player is not None:
                    teams.append(player.team)
                else:
                    flash(f"Player with ID {player_id} not found.")
                    return redirect(url_for("dashboard.select_team", league_id=league_id))
        else:
            # Proceed with saving the team based on the current round
            league = try_get_league_by_id(league_id)
            if league:
                for member in league.member_list:
                    if member.account.id == current_user.id:
                        team_field = f'{current_round}_team'
                        if not getattr(member, team_field, None):
                            fantasy_team = Lineup()
                            fantasy_team.save()
                            setattr(member, team_field, fantasy_team)
                        else:
                            fantasy_team = getattr(member, team_field)

                        # Assign players to the team
                        for position, player_id in player_ids.items():
                            if player_id:
                                setattr(fantasy_team, position, ObjectId(player_id))

                        fantasy_team.save()
                        league.save()
                        break

            return redirect(url_for("dashboard.view_league", league_id=league_id))

    qbs = sorted(Player.objects(position='QB'), key=lambda x: (x.team, x.games_started), reverse=True)
    rbs = sorted(Player.objects(position='RB'), key=lambda x: (x.team, x.games_started), reverse=True)
    wrs = sorted(Player.objects(position='WR'), key=lambda x: (x.team, x.games_started), reverse=True)
    tes = sorted(Player.objects(position='TE'), key=lambda x: (x.team, x.games_started), reverse=True)
    ks = sorted(Player.objects(position='PK'), key=lambda x: (x.team, x.games_started), reverse=True)
    d_sts = sorted(Player.objects(position='D/ST'), key=lambda x: (x.team, x.games_started), reverse=True)

    form.QB.choices = [(qb.id, f"{qb.display_name} ({qb.team})") for qb in qbs]
    form.RB1.choices = form.RB2.choices = [(rb.id, f"{rb.display_name} ({rb.team})") for rb in rbs]
    form.WR1.choices = form.WR2.choices = [(wr.id, f"{wr.display_name} ({wr.team})") for wr in wrs]
    form.TE.choices = [(te.id, f"{te.display_name} ({te.team})") for te in tes]
    form.FLEX.choices = [(flex.id, f"{flex.display_name} ({flex.team})") for flex in sorted(rbs + wrs + tes, key=lambda x: (x.team, x.games_started), reverse=True)]
    # form.K.choices = [(k.id, k.display_name) for k in ks]
    form.K.choices = [(k['id'], f"{k['display_name']} ({k['team']})") for k in ks]
    form.D_ST.choices = [(d_st.id, d_st.display_name) for d_st in d_sts]

    # TODO: Might be able to refactor this by consolidating with some of the code in POST
    league = try_get_league_by_id(league_id)
    if league:
        for member in league.member_list:
            if member.account.id == current_user.id:
                current_team = getattr(member, f'{current_round}_team', None)
                if current_team:
                    form.QB.default = current_team.QB.id
                    form.RB1.default = current_team.RB1.id
                    form.RB2.default = current_team.RB2.id
                    form.WR1.default = current_team.WR1.id
                    form.WR2.default = current_team.WR2.id
                    form.TE.default = current_team.TE.id
                    form.FLEX.default = current_team.FLEX.id
                    form.K.default = current_team.K.id
                    form.D_ST.default = current_team.D_ST.id
                    form.process()
    
    return render_template("select_team.html", form=form)


@bp.route("/league/<league_id>")
@login_required
def view_league(league_id):
    league = try_get_league_by_id(league_id)

    league_members = sorted(league.member_list, key=lambda x: x.account.id == current_user.id, reverse=True)

    team_data = []
    for member in league_members:
        member_data = {
            'owner_name': User.objects(id=member.account.id).first().display_name,
            'team_name': member.team_name,
        }
        
        current_round = current_app.CURRENT_ROUND

        round_team_field = f"{current_round}_team" 
        team = getattr(member, round_team_field, None)
        print(team.D_ST)
        
        for position in ["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "D_ST"]:
            player = getattr(team, position, None) if team else None
            player_name = player.display_name if player else 'Player not set'
            member_data[position] = player_name

        team_data.append(member_data)

    return render_template(
        "view_league.html",
        league=league,
        team_data=team_data,
        positions=["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "D_ST"],
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
            actual_user = current_user._get_current_object()
            # TODO: Make insert operations such that there's no issues if a middle operation fails

            # Create new member object and save to db
            new_member = Member(team_name=team_name, 
                                account=actual_user)

            # Create new league object and save to db
            new_league = League(league_name=league_name, 
                                ruleset=ruleset, 
                                commissioner=actual_user,
                                member_list=[new_member])

            new_league.save()

            # Append new league id to current user's league membership list
            # actual_user.update(push__memberships=new_league)
            # actual_user.reload()
            actual_user.memberships.append(new_league)
            actual_user.save()

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
                                account=current_user.to_dbref())

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