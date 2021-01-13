from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_user, login_required, logout_user, current_user

from .account import Account
from .league import League, Member
from .fantasy_team import FantasyTeam, Player
from .forms import SelectTeamForm

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
    )

@bp.route("/select_team/<league_id>", methods=("GET", "POST"))
@login_required
def select_team(league_id):
    # first game of first week @ Jan 9, 1:05 pm ET -> 6:05 pm UTC
    # if datetime.now(tz.UTC) > datetime(2021, 1, 9, 18, 5, tzinfo=tz.UTC):
    #     e = "Picks have locked for this week"
    #     flash(e)
    #     return redirect(url_for("dashboard.view_league", league_id=league_id))
    week = 2

    form = SelectTeamForm(request.form)
    if request.method == "POST":
        if getattr(form, f'validate_week_{week}')(): # this is so cool
            league = try_get_league_by_id(league_id)
            if league:
                for member in league.member_list:
                    if member.account_id == current_user.id:
                        if not getattr(member, f'week_{week}_team', None):
                            fantasy_team = FantasyTeam()
                            fantasy_team.save()
                            setattr(member, f'week_{week}_team', fantasy_team)
                            league.save()
                        else:
                            fantasy_team = getattr(member, f'week_{week}_team')

                        fantasy_team.QB = ObjectId(form.data["QB"])
                        fantasy_team.RB1 = ObjectId(form.data["RB1"])
                        fantasy_team.RB2 = ObjectId(form.data["RB2"])
                        fantasy_team.WR1 = ObjectId(form.data["WR1"])
                        fantasy_team.WR2 = ObjectId(form.data["WR2"])
                        fantasy_team.TE = ObjectId(form.data["TE"])
                        fantasy_team.FLEX = ObjectId(form.data["FLEX"])
                        fantasy_team.K = ObjectId(form.data["K"])
                        fantasy_team.D_ST = ObjectId(form.data["D_ST"])
                        fantasy_team.save()
                        break

            return redirect(url_for("dashboard.view_league", league_id=league_id))

        else:
            e = "Invalid team composition"
            flash(e)

    qbs = sorted(Player.objects(**{'position': 'QB', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)
    rbs = sorted(Player.objects(**{'position': 'RB', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)
    wrs = sorted(Player.objects(**{'position': 'WR', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)
    tes = sorted(Player.objects(**{'position': 'TE', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)
    ks = sorted(Player.objects(**{'position': 'K', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)
    d_sts = sorted(Player.objects(**{'position': 'D/ST', f'week_{week}_avail': True}), key=lambda x: x.games_started, reverse=True)

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
        'WAS' : ("#7C1415", "#FFB612"),
        'TB' : ("#D50A0A", "#0A0A08"),
        'LAR' : ("#003594", "#FFD100"),
        'CHI' : ("#0B162A", "#C83803"),
    }

    if league.ruleset == "normal":
        default_score_displayed = "score_normal"
    elif league.ruleset == "ppr":
        default_score_displayed = "score_ppr"
    else:
        default_score_displayed = "score_half_ppr"

    data = []

    # TODO: un-hardcode 3
    for week in range(1, 3):
        league_teams = [getattr(member, f'week_{week}_team', None) for member in league_members]
        week_data = []
        if league_teams:
            for position in positions:
                week_data.append([])
                if position == 'D/ST':
                    pos = 'D_ST'
                    score_displayed = 'd_st_score_normal'
                elif position == 'K':
                    pos = position
                    score_displayed = 'k_score_normal'
                else:
                    pos = position
                    score_displayed = default_score_displayed

                for team in league_teams:
                    if team:
                        player = getattr(team, pos)
                        name = player.display_name
                        score = getattr(getattr(player, f'week_{week}_stats'), score_displayed) if getattr(player, f'week_{week}_stats') else Decimal('0.00')
                        colors = team_colors[player.team]
                        week_data[-1].append((name, score, *colors))
                    else:
                        week_data[-1].append(('set your lineup', 0, *team_colors['None']))
        else:
            week_data = [('set your lineup', 0, *team_colors['None'])] * len(positions)
        data.append(week_data)

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