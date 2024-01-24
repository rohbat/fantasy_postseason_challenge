from .config import GAMES
from datetime import datetime
from dateutil import tz

def setup_jinja_env(app):
    app.jinja_env.globals.update(
        zip=zip,
        enumerate=enumerate,
        len=len,
        list=list,
        reversed=reversed
    )

def is_round_locked(round_name):
    current_time = datetime.now(tz.UTC)
    round_start_time = GAMES.get(round_name)['start_time']
    return current_time > round_start_time if round_start_time else False

def calculate_points_from_yds_allowed(yards):
    if yards < 100:
        return 5
    elif 100 <= yards < 200:
        return 3
    elif 200 <= yards < 300:
        return 2
    elif 300 <= yards < 350:
        return 0
    elif 350 <= yards < 400:
        return -1
    elif 400 <= yards < 450:
        return -3
    elif 450 <= yards < 500:
        return -5
    elif 500 <= yards < 550:
        return -6
    else:
        return -7

def calculate_points_from_pts_allowed(points):
    if points == 0:
        return 5
    elif 1 <= points < 6:
        return 4
    elif 7 <= points < 13:
        return 2
    elif 14 <= points < 17:
        return 1
    elif 18 <= points < 27:
        return 0
    elif 28 <= points < 34:
        return -1
    elif 35 <= points < 45:
        return -3
    else:
        return -5

def compute_defensive_fantasy_score(score_obj):
    defensive_touchdowns = int(score_obj['defTD'])
    ints = int(score_obj['defensiveInterceptions'])
    fumbles = int(score_obj['fumblesRecovered'])
    sacks = int(score_obj['sacks'])
    yds = int(score_obj['ydsAllowed'])
    pts = int(score_obj['ptsAllowed'])

    turnover_points = (ints + fumbles) * 2
    yds_pts = calculate_points_from_yds_allowed(yds)
    pt_pts = calculate_points_from_pts_allowed(pts)
    deftd_points = defensive_touchdowns * 6

    return turnover_points + deftd_points + yds_pts + pt_pts

def top_scoring_owner(member_data):
    highest_score = 0.0
    owner_with_highest_score = ""

    for member in member_data:
        if member['lineup_score'] > highest_score:
            highest_score = member['lineup_score']
            owner_with_highest_score = member['owner_name']
        
    return owner_with_highest_score

