from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import *
import configparser

class PlayerStats(EmbeddedDocument):
    pass_yds = IntField()
    pass_td = IntField()
    rush_yds = IntField()
    rush_td = IntField()
    rec_yds = IntField()
    rec_td = IntField()
    rec = IntField()
    pass_int = IntField()
    fumbles = IntField()
    two_pt_conversions = IntField()


    score_normal = DecimalField(precision=2)
    score_half_ppr = DecimalField(precision=2)
    score_ppr = DecimalField(precision=2)

    # Defensive stats
    # Points allowed
    points_allowed = IntField()
    # Defense sacks
    sacks = IntField()
    # Defense interceptions
    def_int = IntField()
    # Defensive ints for TDs
    def_int_td = IntField()
    # Defense fumble recoveries
    fumbles_rec = IntField()
    # Defense fumbles recovered for TDs
    fumbles_rec_td = IntField()
    # Defense safeties (Not currently scraped)
    safeties = IntField()
    # Special teams tds (Not currently scraped)
    st_tds = IntField()
    # Special teams blocked kick (Not currently scraped)
    st_blocked_kicks = IntField()
    # Special teams fumble recovery (Not currently scraped)
    st_fumble_recoveries = IntField()
    
    d_st_score_normal = DecimalField(precision=2)

    # Kicker Stats
    # FG made (0-39 yd)
    fg_0_39 = IntField()
    # FG made (40-49 yd)
    fg_40_49 = IntField()
    # FG made (50-59 yd)
    fg_50_59 = IntField()
    # FG made (60+ yd)
    fg_60 = IntField()
    # FG made
    fgm = IntField()
    # FG attempted
    fga = IntField()
    # PAT Made
    xpm = IntField()
    # PAT Attempted
    xpa = IntField()
    
    k_score_normal = DecimalField(precision=2)

class Player(Document):
    name = StringField(required=True)
    team = StringField(required=True)
    position = StringField(required=True)
    display_name = StringField(required=True)
    games_started = IntField(requred=True, default=0)

    week_1_avail = BooleanField(default=False)
    week_2_avail = BooleanField(default=False)
    week_3_avail = BooleanField(default=False)

    week_1_stats = EmbeddedDocumentField(PlayerStats)
    week_2_stats = EmbeddedDocumentField(PlayerStats)
    week_3_stats = EmbeddedDocumentField(PlayerStats)

    def get_display_name(self):
        return '[' + self.team + '] ' + self.name 

def upload_all_rosters(chrome_driver):
    current_week_teams = ['KC', 'BUF', 'PIT', 'TEN', 'BAL', 'CLE', 'IND', 'GB', 'NO', 'SEA', 'WAS', 'TB', 'LAR', 'CHI']
    url_abbrev_map = {'KC':'kan', 'BUF':'buf', 'PIT':'pit', 'TEN':'oti', 'BAL':'rav', 'CLE':'cle', 'IND':'clt', 
                      'GB':'gnb', 'NO':'nor', 'SEA':'sea', 'WAS':'was', 'TB':'tam', 'LAR':'ram', 'CHI':'chi'}
    team_name_map = {'KC':'Chiefs', 'BUF':'Bills', 'PIT':'Steelers', 'TEN':'Titans', 'BAL':'Ravens', 'CLE':'Browns', 'IND':'Colts',
                     'GB':'Packers', 'NO':'Saints', 'SEA':'Seahawks', 'WAS':'Football Team', 'TB':'Buccaneers', 'LAR':'Rams', 'CHI':'Bears'}

    for team_abbrev in current_week_teams:
        upload_team_roster(chrome_driver, team_abbrev, url_abbrev_map[team_abbrev], team_name_map[team_abbrev])

        # Handle edge cases: for some reason the site doesn't have cooper kupp or alvin kamara?
        if team_abbrev == 'LAR':
            player = Player(name='Cooper Kupp', 
                    team=team_abbrev,
                    position='WR',
                    games_started=16,
                    week_1_avail=True)
            player.display_name = player.get_display_name()
            print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
            player.save()
        
        if team_abbrev == 'NO':
            player = Player(name='Alvin Kamara', 
                    team=team_abbrev,
                    position='RB',
                    games_started=16,
                    week_1_avail=True)
            player.display_name = player.get_display_name()
            print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
            player.save()

def upload_team_roster(chrome_driver, team_abbrev, url_abbrev, team_name):
    week_1_avail = True
    if team_abbrev == 'KC' or team_abbrev == 'GB':
        week_1_avail = False

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
                
                week_1_avail = True
                if team_abbrev == 'KC' or team_abbrev == 'GB':
                    week_1_avail = False

                player = Player(name=name, 
                                team=team_abbrev,
                                position=pos,
                                games_started=games_started,
                                week_1_avail=week_1_avail)
                player.display_name = player.get_display_name()
                print(player.name + ' | ' + player.team + ' | ' + player.position + ' | ' + str(player.games_started) + ' | ' + player.display_name)
                player.save()
    
    player = Player(name=team_name + ' D/ST', 
                    team=team_abbrev,
                    position='D/ST',
                    games_started=16,
                    week_1_avail=week_1_avail)
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