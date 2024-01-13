import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import connect
import configparser
from dotenv import load_dotenv
import requests
import json
from .classes.player import Player
import argparse
from .app import create_app

load_dotenv()

API_URL = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
MONGODB_HOST = f"mongodb+srv://thepaulonascimento:{os.getenv('MONGO_DB_PW')}@postseasonchallenge.drcj3it.mongodb.net/psc_test?retryWrites=true&w=majority"

ApiKey = os.getenv('X-RapidAPI-Key')
ApiHost = os.getenv('X-RapidAPI-Host')

headers = {
    'X-RapidAPI-Key': ApiKey,
    'X-RapidAPI-Host': ApiHost
}

PLAYOFF_TEAMS = ['CLE', 'HOU', 'MIA', 'KC', 'PIT', 'BUF', 'GB', 'DAL', 'LAR', 'DET', 'PHI', 'TB']
desired_positions = {"QB", "WR", "TE", "RB", "K"}

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

# Upload all rosters
def upload_all_rosters():
    all_filtered_rosters = {team: get_filtered_team_roster(team) for team in PLAYOFF_TEAMS}
    for team, roster in all_filtered_rosters.items():
        for player_data in roster:
            # print(player_data)
            player = Player(
                name=player_data['espnName'],
                team=player_data['team'],
                position=player_data['pos'],
                display_name=player_data['longName'],
                games_started=player_data.get('gamesPlayed', 0),
            )
            player.save()

def establish_db_connection():
    mongo_host = MONGODB_HOST
    print(mongo_host)
    if not mongo_host:
        raise ValueError("MongoDB host not found in environment variables")
    try:
        connect(host=mongo_host, alias='psc_test')
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    establish_db_connection()
    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Fantasy Postseason Challenge script")
    parser.add_argument('--mode', type=str, default='app', help="Mode to run the script in ('app' or 'script')")
    args = parser.parse_args()

    # Check the mode and execute accordingly
    if args.mode == 'script':
        print("Running script mode")
        upload_all_rosters()
        print("Rosters uploaded to MongoDB")
    else:
        # Code to run when mode is 'app' or any other value
        # (e.g., initializing and running the Flask app)
        app = create_app()
        app.run()
        pass
