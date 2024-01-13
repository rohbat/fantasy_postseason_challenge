import os
from datetime import datetime
from dateutil import tz
from dotenv import load_dotenv

load_dotenv()

MONGODB_HOST = f"mongodb+srv://thepaulonascimento:{os.getenv('MONGO_DB_PW')}@postseasonchallenge.drcj3it.mongodb.net/"
#psc_test?retryWrites=true&w=majority"

PLAYOFF_START_TIMES = {
    'wildcard': datetime(2024, 1, 13, 13, 5, tzinfo=tz.UTC),
    'divisional': datetime(2024, 1, 20, 13, 5, tzinfo=tz.UTC),
    'championship': datetime(2024, 1, 28, 13, 5, tzinfo=tz.UTC),
}

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
        'host': f"{MONGODB_HOST}psc_prod?retryWrites=true&w=majority"
        'alias': 'psc_prod',
        # Add other connection settings as needed
    }
