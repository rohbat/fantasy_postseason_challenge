from mongoengine import *
import configparser

from roster_db_upload import Player

WEEK = 3
WEEK_3_TEAMS = ['TB', 'GB', 'BUF', 'KC']

def update_week():
    Player.objects(team__in=globals()[f'WEEK_{WEEK}_TEAMS']).update(**{f'set__week_{WEEK}_avail': True})

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config.txt')
    mongo_host = config['DEFAULT']['MONGODB_HOST']
    connect(host=mongo_host)

    update_week()
