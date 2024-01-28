import os

from datetime import datetime
from dateutil import tz
from dotenv import load_dotenv

load_dotenv()

MONGODB_HOST = f"mongodb+srv://thepaulonascimento:{os.getenv('MONGO_DB_PW')}@postseasonchallenge.drcj3it.mongodb.net/"
#psc_test?retryWrites=true&w=majority"

GAMES = {
    'wildcard': {
        'start_time': datetime(2024, 1, 15, 13, 5, tzinfo=tz.UTC), 
        'game_ids': ['20240113_CLE@HOU', '20240113_MIA@KC', '20240114_GB@DAL', '20240114_LAR@DET', '20240115_PIT@BUF', '20240115_PHI@TB'],
        'playoff_teams': ['CLE', 'HOU', 'KC', 'BUF', 'GB', 'MIA', 'DET', 'TB', 'PHI', 'LAR']
    },
    'divisional': {
        'start_time': datetime(2024, 1, 20, 13, 5, tzinfo=tz.UTC), 
        'game_ids': ['20240120_GB@SF','20240120_HOU@BAL','20240121_TB@DET','20240121_KC@BUF'],
        'playoff_teams': ['BAL', 'HOU', 'KC', 'BUF', 'GB', 'SF', 'DET', 'TB']
    },
    'championship': {
        'start_time': datetime(2024, 1, 28, 13, 5, tzinfo=tz.UTC), 
        # 'game_ids': ['20240128_KC@BAL', '20240128_DET@SF'],
        'game_ids' : ['20240128_KC@BAL'],
        'playoff_teams': ['BAL', 'KC', 'SF', 'DET']
    },
}

# CHANGE THIS TO UPDATE ROUND
CURRENT_ROUND = 'championship'

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False
    # Define other global settings

class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'host': f"{MONGODB_HOST}psc_test?retryWrites=true&w=majority",  # Read from .env file
        'alias': 'psc_test',
        # Add other connection settings as needed
    }

class ProductionConfig(Config):
    # Production specific configuration
    MONGODB_SETTINGS = {
        'host': f"{MONGODB_HOST}psc_prod?retryWrites=true&w=majority",
        'alias': 'psc_prod',
        # Add other connection settings as needed
    }

def get_db_alias():
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        return ProductionConfig.MONGODB_SETTINGS['alias']
    else:
        return DevelopmentConfig.MONGODB_SETTINGS['alias']
