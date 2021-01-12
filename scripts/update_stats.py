from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import *
import shutil
import configparser
import pandas as pd

from roster_db_upload import Player, PlayerStats

# WEEK 1
GAMES_TO_COLLECT = [
    '202101090buf',
    '202101090sea',
    '202101090was',
    '202101100nor',
    '202101100oti',
    '202101100pit',
]

def collect_scores(game_code, chrome_driver):
    url = f"https://www.pro-football-reference.com/boxscores/{game_code}.htm"

    chrome_driver.get(url)
    # html.parser slower than lxml, but no extra dependencies and should be fine
    soup = bs(chrome_driver.page_source, "html.parser")
    collect_offensive_scores(soup)
    collect_defensive_scores(soup)
    collect_kicker_scores(soup)

def collect_offensive_scores(soup):
    offense_table = soup.find("table", {"id":"player_offense"})
    rows = offense_table.find_all("tr")

    for row in rows:
        name = row.a
        if not name:
            continue

        name = name.text.strip()
        team = row.find("td", {"data-stat": "team"}).text
        print(name + ' | ' + team)
        
        stat_list = ["pass_yds", "pass_td", "rush_yds", "rush_td",
            "rec_yds", "rec_td", "rec", "pass_int", "fumbles"]
        stats = {
            stat: int(row.find('td', {'data-stat': stat}).text)
            for stat in stat_list
        }

        scores = compute_offense_score(**stats)
        stats["score_normal"] = scores[0]
        stats["score_half_ppr"] = scores[1]
        stats["score_ppr"] = scores[2]

        print(stats)

        player_stats = PlayerStats(**stats)
        update_player_stats(name, team, player_stats)

def collect_defensive_scores(soup):
    scoring_table = soup.find("table", {"id":"scoring"})

    # Get home and away team
    vis_team = scoring_table.find("th", {"data-stat":"vis_team_score"}).text
    home_team = scoring_table.find("th", {"data-stat":"home_team_score"}).text

    vis_team_def_stats = {}
    home_team_def_stats = {}

    defense_table = soup.find('table', {'id': 'player_defense'})
    # df_ugly is table as parsed by pd, df is table with correct columns that can
    # be summed by team and directly converted to dict of desired values
    df_ugly = pd.read_html(str(defense_table))[0]
    df = pd.DataFrame()
    df['team'] = df_ugly['Unnamed: 1_level_0']['Tm']
    df['def_int_td'] = df_ugly['Def Interceptions']['TD']
    df['fumbles_rec_td'] = df_ugly['Fumbles']['TD']
    df['sacks'] = df_ugly['Unnamed: 7_level_0']['Sk']
    df['def_int'] = df_ugly['Def Interceptions']['Int']
    df['fumbles_rec'] = df_ugly['Fumbles']['FR']
    df.dropna(axis=0, inplace=True)
    df = df[df.team != 'Tm']
    df = df.astype({
        'def_int_td': int,
        'fumbles_rec_td': int,
        'sacks': float,
        'def_int': int,
        'fumbles_rec': int
    })

    vis_team_def_stats.update(dict(df[df.team==vis_team].sum()))
    home_team_def_stats.update(dict(df[df.team==home_team].sum()))
    vis_team_def_stats.pop('team')
    home_team_def_stats.pop('team')

    # Get home and away points allowed
    final_score = scoring_table.find_all("tr")[-1]
    vis_team_def_stats['points_allowed'] = int(final_score.find('td', {'data-stat':'home_team_score'}).text)
    home_team_def_stats['points_allowed'] = int(final_score.find('td', {'data-stat':'vis_team_score'}).text)
    # correct for defensive touchdowns
    vis_team_def_stats['points_allowed'] -= 6 * (home_team_def_stats['def_int_td'] + home_team_def_stats['fumbles_rec_td'])
    home_team_def_stats['points_allowed'] -= 6 * (vis_team_def_stats['def_int_td'] + vis_team_def_stats['fumbles_rec_td'])

    vis_team_def_stats['d_st_score_normal'] = compute_defense_score(**vis_team_def_stats)
    home_team_def_stats['d_st_score_normal'] = compute_defense_score(**home_team_def_stats)


    web_db_team_name_map = {'KAN':'KC', 'GNB':'GB', 'NOR':'NO', 'TAM':'TB'}
    team_name_map = {'KC':'Chiefs', 'BUF':'Bills', 'PIT':'Steelers', 'TEN':'Titans', 'BAL':'Ravens', 'CLE':'Browns', 'IND':'Colts',
                     'GB':'Packers', 'NO':'Saints', 'SEA':'Seahawks', 'WAS':'Football Team', 'TB':'Buccaneers', 'LAR':'Rams', 'CHI':'Bears'}

    vis_player_stats = PlayerStats(**vis_team_def_stats)
    home_player_stats = PlayerStats(**home_team_def_stats)

    vis_team_full = team_name_map[web_db_team_name_map.get(vis_team, vis_team)]
    update_player_stats(f'{vis_team_full} D/ST', vis_team, vis_player_stats)
    home_team_full = team_name_map[web_db_team_name_map.get(home_team, home_team)]
    update_player_stats(f'{home_team_full} D/ST', home_team, home_player_stats)  
    
    print(f'{vis_team_full} D/ST', '|', vis_team)
    print(vis_team_def_stats)
    print(f'{home_team_full} D/ST', '|', home_team)
    print(home_team_def_stats)

def collect_kicker_scores(soup):
    kicking_table = soup.find("table", {"id":"kicking"})
    rows = kicking_table.find_all("tr")

    # Stats to scrape directly and FG distance stats to compute
    stat_scrape_list = ['xpm', 'xpa', 'fgm', 'fga']
    stat_fg_yard_list = ['fg_0_39', 'fg_40_49', 'fg_50_59', 'fg_60']
    for row in rows:
        name = row.a
        if not name:
            continue
        if row.find('td', {'data-stat': 'xpa'}).text == '' and row.find('td', {'data-stat': 'fga'}).text == '':
            continue
        
        name = name.text.strip()
        team = row.find("td", {"data-stat": "team"}).text
        print(name + ' | ' + team)
        
        # Scrape all basic stats
        stats = {}
        for stat in stat_scrape_list:
            stat_val = row.find('td', {'data-stat': stat}).text
            
            stats[stat] = int(stat_val) if stat_val != '' else 0
        
        # Get length of all FGs made
        fg_yards = []
        scoring_table = soup.find("table", {"id":"scoring"})
        scoring_rows = scoring_table.find_all("tr")
        
        for score in scoring_rows:
            if not score.find('td', {'data-stat':'description'}):
                continue
                
            if score.find('td', {'data-stat':'description'}).a.text == name:
                fg_yards.append(int(score.find('td', {'data-stat':'description'}).text.strip()[len(name)+1:len(name)+3]))
        
        # Bucket all FG distances
        for fg_yard_stat in stat_fg_yard_list:
            stats[fg_yard_stat] = 0 
        
        for fg_yard in fg_yards:
            if fg_yard < 40:
                stats['fg_0_39'] += 1
            elif fg_yard < 50:
                stats['fg_40_49'] += 1
            elif fg_yard < 60:
                stats['fg_50_59'] += 1
            else:
                stats['fg_60'] += 1
        
        kicker_score = compute_kicker_score(**stats)
        stats["k_score_normal"] = kicker_score

        print(stats)

        player_stats = PlayerStats(**stats)
        update_player_stats(name, team, player_stats)


def compute_offense_score(
    pass_yds=0,
    pass_td=0,
    rush_yds=0,
    rush_td=0,
    rec_yds=0,
    rec_td=0,
    rec=0,
    pass_int=0,
    fumbles=0,
):

    base_score =  (
        (pass_yds * 0.04)
        + (pass_td * 4)
        + (rush_yds * 0.1)
        + (rush_td * 6)
        + (rec_yds * 0.1)
        + (rec_td * 6)
        - (pass_int * 2)
        - (fumbles * 2)
    )

    return (
        round(base_score, 2),               # NORMAL
        round(base_score + (rec * 0.5), 2), # 0.5PPR
        round(base_score + rec, 2)          # PPR
    )

def compute_defense_score(
    points_allowed=0,
    sacks=0,
    def_int=0,
    def_int_td=0,
    fumbles_rec=0,
    fumbles_rec_td=0,
):
    points_allowed_points = 0

    if points_allowed == 0:
        points_allowed_points = 10
    elif points_allowed < 7:
        points_allowed_points = 7
    elif points_allowed < 14:
        points_allowed_points = 4
    elif points_allowed < 21:
        points_allowed_points = 1
    elif points_allowed < 28:
        points_allowed_points = 0
    elif points_allowed < 35:
        points_allowed_points = -1
    else:
        points_allowed_points = -4

    score =  (
        points_allowed_points
        + sacks
        + (def_int * 2)
        + (def_int_td * 6)
        + (fumbles_rec * 2)
        + (fumbles_rec_td * 6)
    )

    return score

def compute_kicker_score(
    fg_0_39=0,
    fg_40_49=0,
    fg_50_59=0,
    fg_60=0,
    fgm=0,
    fga=0,
    xpm=0,
    xpa=0,
):

    score =  (
        (fg_0_39 * 3)
        + (fg_40_49 * 4)
        + (fg_50_59 * 5)
        + (fg_60 * 5)
        + xpm
    )

    return score

def update_player_stats(name, team, player_stats):
    # Team abbreviations aren't the same between the site we scrape and the DB. 
    # This map from web name to db name handles any inconsistencies.
    web_db_team_name_map = {'KAN':'KC', 'GNB':'GB', 'NOR':'NO', 'TAM':'TB'}

    db_team_name = web_db_team_name_map[team] if team in web_db_team_name_map else team
    
    # TODO: hard coded week 1
    Player.objects(name=name, team=db_team_name).update_one(set__week_1_stats=player_stats)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('./config.txt')
    mongo_host = config['DEFAULT']['MONGODB_HOST']
    connect(host=mongo_host)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    chrome_driver_path = shutil.which("chromedriver")
    chrome_driver = webdriver.Chrome(options=options, executable_path=chrome_driver_path)


    week = 1
    for game in GAMES_TO_COLLECT:
        collect_scores(game, chrome_driver)

    chrome_driver.close()
