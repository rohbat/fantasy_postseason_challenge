from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import *
import configparser

class Player(Document):
    name = StringField(required=True)
    team = StringField(required=True)
    position = StringField(required=True)
    display_name = StringField(required=True)
    games_started = IntField(requred=True, default=0)

    week_1_avail = BooleanField(default=False)
    week_2_avail = BooleanField(default=False)
    week_3_avail = BooleanField(default=False)

    def get_display_name(self):
        return '[' + self.team + '] ' + self.name 

def upload_all_rosters(chrome_driver):
    current_week_teams = ['KC', 'BUF', 'PIT', 'GB', 'NO', 'SEA', 'TB']
    url_abbrev_map = {'KC':'kan', 'BUF':'buf', 'PIT':'pit', 'GB':'gnb', 'NO':'nor', 'SEA':'sea', 'TB':'tam'}
    team_name_map = {'KC':'Chiefs', 'BUF':'Bills', 'PIT':'Steelers', 'GB':'Packers', 'NO':'Saints', 'SEA':'Seahawks', 'TB':'Buccaneers'}

    for team_abbrev in current_week_teams:
        upload_team_roster(chrome_driver, team_abbrev, url_abbrev_map[team_abbrev], team_name_map[team_abbrev])

def upload_team_roster(chrome_driver, team_abbrev, url_abbrev, team_name):
    URL = 'https://www.pro-football-reference.com/teams/' + url_abbrev + '/2020_roster.htm'
    chrome_driver.get(URL)

    soup = bs(chrome_driver.page_source)
    roster_table = soup.find("table", {"id":"games_played_team"}).find('tbody')

    positions = ['QB', 'RB', 'WR', 'TE', 'K']

    rows = roster_table.find_all('tr')

    for row in rows:
        pos_find = row.find('td', {'data-stat':'pos'})
        if pos_find:
            pos = pos_find.text.strip()
            
            if pos in positions:
                name = row.find('td', {'data-stat':'player'}).text.strip()
                games_started_text = row.find('td', {'data-stat':'gs'}).text.strip()
                games_started = 0
                if games_started_text:
                    games_started = int(games_started_text)
                
                player = Player(name=name, 
                                team=team_abbrev,
                                position=pos,
                                games_started=games_started,
                                week_1_avail=True)
                player.display_name = player.get_display_name()
                print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
                player.save()
    
    player = Player(name=team_name + ' D/ST', 
                    team=team_abbrev,
                    position='D/ST',
                    games_started=16,
                    week_1_avail=True)
    player.display_name = player.get_display_name()
    print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
    player.save()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('./config.txt')
    mongo_host = config['DEFAULT']['MONGODB_HOST']
    connect(host=mongo_host)
    
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    chrome_driver = webdriver.Chrome(options=options)

    upload_all_rosters(chrome_driver)

    chrome_driver.close()