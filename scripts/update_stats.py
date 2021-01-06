from selenium import webdriver
from bs4 import BeautifulSoup as bs
from mongoengine import *
import shutil

def collect_scores(chrome_driver):
    game_code = "202101030cle"
    url = f"https://www.pro-football-reference.com/boxscores/{game_code}.htm"

    chrome_driver.get(url)
    # html.parser slower than lxml, but no extra dependencies and should be fine
    soup = bs(chrome_driver.page_source, "html.parser")

    offense_table = soup.find("table", {"id":"player_offense"})
    rows = offense_table.find_all("tr")

    for row in rows:
        player = row.a
        if not player:
            continue

        player = player.text.strip()
        stat_list = ["pass_yds", "pass_td", "rush_yds", "rush_td",
            "rec_yds", "rec_td", "rec", "pass_int", "fumbles"]

        stat_values = {
            stat: int(row.find('td', {'data-stat': stat}).text)
            for stat in stat_list
        }

        print(player, offense_score(**stat_values))        




def offense_score(
    pass_yds=0,
    pass_td=0,
    rush_yds=0,
    rush_td=0,
    rec_yds=0,
    rec_td=0,
    # ppr_multiplier=0,
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
        # + (rec * ppr_multiplier)
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
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    chrome_driver_path = shutil.which("chromedriver")
    chrome_driver = webdriver.Chrome(options=options, executable_path=chrome_driver_path)

    collect_scores(chrome_driver)

    chrome_driver.close()
