from mongoengine import *
import configparser

from roster_db_upload import Player

WEEK_2_TEAMS = ['KC', 'BUF', 'BAL', 'CLE', 'GB', 'NO', 'TB', 'LAR']

def update_week_2():
    Player.objects(team__in=WEEK_2_TEAMS).update(set__week_2_avail=True)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config.txt')
    mongo_host = config['DEFAULT']['MONGODB_HOST']
    connect(host=mongo_host)

    update_week_2()
