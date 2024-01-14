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

from bson.objectid import ObjectId

from datetime import datetime
from dateutil import tz
from decimal import Decimal

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route("/homepage")
@login_required
def logged_in_homepage():
    league_memberships = current_user.memberships
    team_names = []
    league_commissionerships = []

    for league_membership in league_memberships:
        for member in league_membership.member_list:
            if member.account.id == current_user.id:
                team_names.append(member.team_name)
                break
        if league_membership.commissioner.id == current_user.id:
            league_commissionerships.append(league_membership)

    return render_template(
        "logged_in_homepage.html",
        league_memberships=league_memberships,
        team_names=team_names,
        league_commissionerships=league_commissionerships,
    )

@bp.route("/select_team/<league_id>", methods=("GET", "POST"))
@login_required
def select_team(league_id):
    current_round = 'wildcard'  # Determine the current round programmatically or from user input

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
            "D/ST": form.data["D_ST"]
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

    form.QB.choices = [(qb.id, qb.display_name) for qb in qbs]
    form.RB1.choices = form.RB2.choices = [(rb.id, rb.display_name) for rb in rbs]
    form.WR1.choices = form.WR2.choices = [(wr.id, wr.display_name) for wr in wrs]
    form.TE.choices = [(te.id, te.display_name) for te in tes]
    form.FLEX.choices = [(flex.id, flex.display_name) for flex in sorted(rbs + wrs + tes, key=lambda x: (x.team, x.games_started), reverse=True)]
    # form.K.choices = [(k.id, k.display_name) for k in ks]
    form.K.choices = [(k['id'], k['display_name']) for k in ks]
    form.D_ST.choices = [(d_st.id, d_st.display_name) for d_st in d_sts]

    # TODO: Might be able to refactor this by consolidating with some of the code in POST
    league = try_get_league_by_id(league_id)
    if league:
        for member in league.member_list:
            if member.account.id == current_user.id:
                current_team = getattr(member, f'week_{week}_team', None)
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

    league_members = league.member_list
    league_members = sorted(league_members, key=lambda x: x.account.id == current_user.id, reverse=True)

    team_names = [member.team_name for member in league_members]
    member_names = [User.objects(id=member.account.id).first().display_name for member in league_members]

    positions = ["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "D_ST"]
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
        'WAS' : ("#7C1415", "#FFB612"),
        'TB' : ("#D50A0A", "#0A0A08"),
        'LAR' : ("#003594", "#FFD100"),
        'CHI' : ("#0B162A", "#C83803"),
    }

    lineup_data = []
    team_scores = []
    playoff_scores = []
    player_score_memo = {}

    if league.ruleset == "normal":
        default_score_displayed = "score_normal"
    elif league.ruleset == "ppr":
        default_score_displayed = "score_ppr"
    else:
        default_score_displayed = "score_half_ppr"

    current_round = current_app.CURRENT_ROUND
    round_team_field = f"{current_round}_team" 

    league_teams = [getattr(member, round_team_field, None) for member in league_members]
    
    week_data = []
    if league_teams:
        week_scores = [Decimal(0.00) for _ in league_teams]

        for position in positions:
            week_data.append([])
            if position == 'D_ST':
                pos = 'D_ST'
                score_displayed = 'd_st_score_normal'
            elif position == 'K':
                pos = position
                score_displayed = 'k_score_normal'
            else:
                pos = position
                score_displayed = default_score_displayed
            for i, team in enumerate(league_teams):
                if team:
                    player = getattr(team, position)
                    name = player.display_name if player else 'Player not set'

                    # Assuming the score calculation logic is based on a method in your player class
                    # score = player.calculate_score_for_round(current_round) if player else Decimal('0.00')
                    score = Decimal('0.00')

                    colors = team_colors.get(player.team, ("#808080", "#FF00FF")) if player else team_colors['None']
                    week_data[-1].append((name, score, *colors))
                    week_scores[i] += score
                else:
                    week_data[-1].append(('set your lineup', 0, *team_colors['None']))
    else:
        week_data = [('set your lineup', 0, *team_colors['None'])] * len(positions)
    
    lineup_data.append(week_data)
    team_scores.append(week_scores)

    # Calculate scores only for the current round
    playoff_scores = [score for score in week_scores]

    return render_template(
        "view_league.html",
        positions=positions,
        team_names=team_names,
        member_names=member_names,
        lineup_data=lineup_data,
        team_scores=team_scores,
        playoff_scores=playoff_scores,
        league=league,
        position_width=60,
        score_width=50, # TODO: choose good values for these and put in html?
        name_width=180, # TODO: choose good values for these and put in html?
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
                                account=current_user.to_dbref())

            # Create new league object and save to db
            new_league = League(league_name=league_name, 
                                ruleset=ruleset, 
                                commissioner=current_user.to_dbref(),
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