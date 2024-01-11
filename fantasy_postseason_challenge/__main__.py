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
    # # Writing the results to a JSON file
    # with open('results.json', 'w') as file:
    #     json.dump(all_filtered_rosters, file, indent=4)
    #     print("Rosters saved to results.json")

# Main execution
# if __name__ == "__main__":
#     mongo_host = os.getenv('MONGODB_HOST')
#     connect(host=mongo_host, alias='psc_test')
#     upload_all_rosters()
#     print("Rosters uploaded to MongoDB")

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

# def upload_all_rosters(chrome_driver):
#     current_week_teams = ['KC', 'BUF', 'PIT', 'TEN', 'BAL', 'CLE', 'IND', 'GB', 'NO', 'SEA', 'WAS', 'TB', 'LAR', 'CHI']
#     url_abbrev_map = {'KC':'kan', 'BUF':'buf', 'PIT':'pit', 'TEN':'oti', 'BAL':'rav', 'CLE':'cle', 'IND':'clt', 
#                       'GB':'gnb', 'NO':'nor', 'SEA':'sea', 'WAS':'was', 'TB':'tam', 'LAR':'ram', 'CHI':'chi'}
#     team_name_map = {'KC':'Chiefs', 'BUF':'Bills', 'PIT':'Steelers', 'TEN':'Titans', 'BAL':'Ravens', 'CLE':'Browns', 'IND':'Colts',
#                      'GB':'Packers', 'NO':'Saints', 'SEA':'Seahawks', 'WAS':'Football Team', 'TB':'Buccaneers', 'LAR':'Rams', 'CHI':'Bears'}

#     for team_abbrev in current_week_teams:
#         upload_team_roster(chrome_driver, team_abbrev, url_abbrev_map[team_abbrev], team_name_map[team_abbrev])

       

# def upload_team_roster(chrome_driver, team_abbrev, url_abbrev, team_name):
#     week_1_avail = True
#     if team_abbrev == 'KC' or team_abbrev == 'GB':
#         week_1_avail = False

#     URL = 'https://www.pro-football-reference.com/teams/' + url_abbrev + '/2020_roster.htm'
#     chrome_driver.get(URL)

#     soup = bs(chrome_driver.page_source)
#     roster_table = soup.find("table", {"id":"games_played_team"}).find('tbody')

#     positions = ['QB', 'RB', 'WR', 'TE', 'K']

#     rows = roster_table.find_all('tr')

#     for row in rows:
#         pos_find = row.find('td', {'data-stat':'pos'})
#         if pos_find:
#             pos = pos_find.text.strip()
            
#             if pos in positions:
#                 name = row.find('td', {'data-stat':'player'}).text.strip()
#                 games_started_text = row.find('td', {'data-stat':'gs'}).text.strip()
#                 games_started = 0
#                 if games_started_text:
#                     games_started = int(games_started_text)
                
#                 week_1_avail = True
#                 if team_abbrev == 'KC' or team_abbrev == 'GB':
#                     week_1_avail = False

#                 player = Player(name=name, 
#                                 team=team_abbrev,
#                                 position=pos,
#                                 games_started=games_started,
#                                 week_1_avail=week_1_avail)
#                 player.display_name = player.get_display_name()
#                 print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
#                 player.save()
    
#     player = Player(name=team_name + ' D/ST', 
#                     team=team_abbrev,
#                     position='D/ST',
#                     games_started=16,
#                     week_1_avail=week_1_avail)
#     player.display_name = player.get_display_name()
#     print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
#     player.save()

# if __name__ == "__main__":
#     config = configparser.ConfigParser()
#     config.read('./config.txt')
#     mongo_host = config['DEFAULT']['MONGODB_HOST']
#     connect(host=mongo_host)
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('headless')
#     chrome_driver = webdriver.Chrome(options=options)

#     upload_all_rosters(chrome_driver)

#     chrome_driver.close()