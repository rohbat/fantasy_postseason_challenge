import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from .config import DevelopmentConfig, ProductionConfig, get_db_alias, GAMES
from mongoengine import connect
from .utilities import extract_teams_from_game_id, compute_defensive_fantasy_score
import configparser
from dotenv import load_dotenv
import requests
import json
from .classes.player import Player, Scores
import argparse
from .app import create_app

from bson.dbref import DBRef
from pymongo import MongoClient

load_dotenv()

API_URL = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
MONGODB_HOST = f"mongodb+srv://thepaulonascimento:{os.getenv('MONGO_DB_PW')}@postseasonchallenge.drcj3it.mongodb.net/{get_db_alias()}?retryWrites=true&w=majority"

ApiKey = os.getenv('X-RapidAPI-Key')
ApiHost = os.getenv('X-RapidAPI-Host')

client = MongoClient(MONGODB_HOST)
db = client['psc_test']

headers = {
    'X-RapidAPI-Key': ApiKey,
    'X-RapidAPI-Host': ApiHost
}

#TODO: move to config and put behind GAMES dict
PLAYOFF_TEAMS = ['BAL', 'HOU', 'KC', 'BUF', 'GB', 'SF', 'DET','TB']

desired_positions = {"QB", "WR", "TE", "RB", "PK"}

# Function to get filtered team roster
def get_filtered_team_roster(team_abv):
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

#TODO: Refactor
def grab_scores_for_games(game_ids):
    for id in game_ids:
        try:
            url = f"{API_URL}/getNFLBoxScore"
            response = requests.get(url, params={'gameID': id, 'fantasyPoints': True}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                player_stats = data['body']['playerStats']
                for index in player_stats:
                    # Process each player's stats here
                    player_obj = player_stats[index]
                    name = player_obj['longName']
                    team = player_obj['team']

                    if player_obj.get('fantasyPointsDefault') is not None:
                        existing_player = Player.objects(name=name, team=team).first()
                        if existing_player:
                            fpoints = player_obj['fantasyPointsDefault']
                            scores = Scores(standard = fpoints['standard'],
                                            half_ppr = fpoints['halfPPR'],
                                            ppr = fpoints['PPR'])

                            #TODO: replace with code grabbing current round
                            if existing_player.position != "PK":
                                existing_player.playoff_scores["divisional"] = scores
                                existing_player.save()
                                print(f"Updated db record for {name}")

                dst_scores = data['body']['DST']
                for score in dst_scores:
                    team_score = dst_scores[score]
                    abv = team_score['teamAbv']
                    team_defense = f"{abv} D/ST"

                    defense_in_db = Player.objects(name=team_defense, team=abv).first()
                    computed = compute_defensive_fantasy_score(team_score)
                    tosave = Scores(standard=computed,half_ppr=computed,ppr=computed)

                    #TODO: replace with code grabbing current round
                    defense_in_db.playoff_scores["divisional"] = tosave
                    defense_in_db.save()
                    print(f"Saved {team_score['teamAbv']} D/ST: {compute_defensive_fantasy_score(team_score)} pts")
            else:
                print(f"Failed to fetch data for game ID {id}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error during request for game ID {id}: {e}")

# Upload all rosters
def upload_all_rosters():
    all_filtered_rosters = {team: get_filtered_team_roster(team) for team in PLAYOFF_TEAMS}
    all_players_data = []
    for team, roster in all_filtered_rosters.items():
        for player_data in roster:
            if player_data.get('espnHeadshot') is not None:
                print(player_data['espnHeadshot'])
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
            all_players_data.append(player_data)
        json_output = json.dumps(all_players_data, indent=4)

    # If you want to save this JSON data to a file
    with open('players_data.json', 'w') as file:
        file.write(json_output)

def establish_db_connection():
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        mongo_host = ProductionConfig.MONGODB_SETTINGS['host']
        mongo_alias = ProductionConfig.MONGODB_SETTINGS['alias']
    else:
        mongo_host = DevelopmentConfig.MONGODB_SETTINGS['host']
        mongo_alias = DevelopmentConfig.MONGODB_SETTINGS['alias']

    print(f"Connecting to MongoDB: {mongo_host}")
    if not mongo_host:
        raise ValueError("MongoDB host not found in environment variables")
    try:
        connect(host=mongo_host, alias=mongo_alias)
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    establish_db_connection()
    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Fantasy Postseason Challenge script")
    parser.add_argument('--mode', type=str, default='app', help="Mode to run the script in ('upload' or 'scores')")
    args = parser.parse_args()

    # Check the mode and execute accordingly
    if args.mode == 'upload':
        print("Running DB upload mode")
        upload_all_rosters()
        print("Rosters uploaded to MongoDB")
    elif args.mode == 'scores':
        #TODO: Update to grab round programmatically
        game_ids = ['20240120_HOU@BAL', '20240120_GB@SF', '20240121_TB@DET']
        # game_ids = GAMES['divisional']['game_ids']
        grab_scores_for_games(game_ids)
    else:
        # Code to run when mode is 'app' or any other value
        # (e.g., initializing and running the Flask app)
        app = create_app()
        app.run()
        pass
