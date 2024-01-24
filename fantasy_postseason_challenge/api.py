import os
import sys
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from .config import GAMES, CURRENT_ROUND, get_db_alias
from .classes.player import Player, Scores
from .utilities import compute_defensive_fantasy_score

from dotenv import load_dotenv

load_dotenv()

API_URL = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
MONGODB_HOST = f"mongodb+srv://thepaulonascimento:{os.getenv('MONGO_DB_PW')}@postseasonchallenge.drcj3it.mongodb.net/{get_db_alias()}?retryWrites=true&w=majority"

ApiKey = os.getenv('X-RapidAPI-Key')
ApiHost = os.getenv('X-RapidAPI-Host')

headers = {
    'X-RapidAPI-Key': ApiKey,
    'X-RapidAPI-Host': ApiHost
}

# Function to get filtered team roster
def get_filtered_team_roster(team_abv):
    desired_positions = ["QB", "WR", "TE", "RB", "PK"]

    url = f"{API_URL}/getNFLTeamRoster?teamAbv={team_abv}&getStats=true"
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        team_roster = data['body']['roster']
    except (ValueError, KeyError) as e:
        print("Error parsing JSON or accessing keys:", e)
        return []

    filtered_roster = [player for player in team_roster if player["pos"] in desired_positions]

    # Add D/ST player
    dst_player = {
        "espnName": f"{team_abv} D/ST",
        "longName": f"{team_abv} D/ST",
        "team": team_abv,
        "pos": "D/ST",
        "games_started": 16
    }
    filtered_roster.append(dst_player)

    return filtered_roster

    # Upload all rosters
def upload_all_rosters():
    team_list = GAMES[CURRENT_ROUND]['playoff_teams']

    all_filtered_rosters = {team: get_filtered_team_roster(team) for team in team_list}

    for team, roster in all_filtered_rosters.items():
        for player_data in roster:
            player = Player(
                name=player_data['espnName'],
                team=player_data['team'],
                position=player_data['pos'],
                display_name=player_data['longName'],
                games_started=player_data.get('gamesPlayed', 0),
                headshot_url=player_data['espnHeadshot'] if player_data.get('espnHeadshot') is not None else ''
            )

            existing_player = Player.objects(name=player.name, team=player.team).first()

            if existing_player is None:
                # If the player does not exist, save the new player
                player.save()
            else:
                # Otherwise update existing player data
                existing_player.update(
                    set__position=player.position,
                    set__display_name=player.display_name,
                    set__games_started=player.games_started,
                    set__headshot_url=player.headshot_url
                )
                pass

# ================================

def save_dst_scores(dst_scores):
    for score in dst_scores:
        team_score = dst_scores[score]
        abv = team_score['teamAbv']
        dst_string = f"{abv} D/ST"

        # Grab D/ST object from DB
        defense_in_db = Player.objects(name=dst_string, team=abv).first()
        computed = compute_defensive_fantasy_score(team_score)
        new_score = Scores(standard=computed,half_ppr=computed,ppr=computed)

        defense_in_db.playoff_scores[CURRENT_ROUND] = new_score
        defense_in_db.save()

        print(f"Saved {abv} D/ST: {compute_defensive_fantasy_score(team_score)} pts")

def upload_player_score(player_obj):
    name = player_obj['longName']
    team = player_obj['team']

    # Weeds out defensive players since this obj doesn't have a position field
    if player_obj.get('fantasyPointsDefault') is not None:
        existing_player = Player.objects(name=name, team=team).first()
        if existing_player:
            fantasy_points = player_obj['fantasyPointsDefault']
            scores = Scores(standard = fantasy_points['standard'],
                            half_ppr = fantasy_points['halfPPR'],
                            ppr = fantasy_points['PPR'])

            # API doesn't provide correct kicker data so it's uploaded manually
            if existing_player.position != "PK":
                existing_player.playoff_scores[CURRENT_ROUND] = scores
                existing_player.save()
                print(f"Updated db record for {name}")


def grab_scores_for_games(game_ids):
    for id in game_ids:
        try:
            url = f"{API_URL}/getNFLBoxScore"
            response = requests.get(url, params={'gameID': id, 'fantasyPoints': True}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Gives the stats for every player in a given game
                all_player_stats = data['body']['playerStats']

                for player in all_player_stats:
                    # Process each player's stats here
                    upload_player_score(all_player_stats[player])

                #API gives team defensive stats as home & away in DST obj
                save_dst_scores(data['body']['DST'])

            else:
                print(f"Failed to fetch data for game ID {id}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error during request for game ID {id}: {e}")