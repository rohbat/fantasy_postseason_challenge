from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import *
import shutil
import configparser

from roster_db_upload import Player, PlayerStats

# TODO: edit with correct games
GAMES_TO_COLLECT = ["202101030cle"]

def collect_scores(game_code, chrome_driver):
    url = f"https://www.pro-football-reference.com/boxscores/{game_code}.htm"

    chrome_driver.get(url)
    # html.parser slower than lxml, but no extra dependencies and should be fine
    soup = bs(chrome_driver.page_source, "html.parser")

    offense_table = soup.find("table", {"id":"player_offense"})
    rows = offense_table.find_all("tr")

    for row in rows:
        name = row.a
        if not name:
            continue

        name = name.text.strip()
        stat_list = ["pass_yds", "pass_td", "rush_yds", "rush_td",
            "rec_yds", "rec_td", "rec", "pass_int", "fumbles"]
        stats = {
            stat: int(row.find('td', {'data-stat': stat}).text)
            for stat in stat_list
        }
        team = row.find("td", {"data-stat": "team"}).text

        scores = offense_score(**stats)
        stats["score_normal"] = scores[0]
        stats["score_half_ppr"] = scores[1]
        stats["score_ppr"] = scores[2]

        player_stats = PlayerStats(**stats)

        # TODO: hard coded week 1
        Player.objects(name=name, team=team).update_one(set__week_1_stats=player_stats)
        # this assumes unique name/team pairs

def offense_score(
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

def defense_stats():
    pass

def kicker_stats():
    pass

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
