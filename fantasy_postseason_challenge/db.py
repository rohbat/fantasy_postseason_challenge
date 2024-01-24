import os
import sys

from flask_mongoengine import MongoEngine
from mongoengine import connect
from .config import DevelopmentConfig, ProductionConfig

db = MongoEngine()

def initialize_db(app):
    db.init_app(app)

def establish_db_connection():
    flask_env = os.getenv('FLASK_ENV', 'development')

    if flask_env == 'production':
        mongo_host = ProductionConfig.MONGODB_SETTINGS['host']
        mongo_alias = ProductionConfig.MONGODB_SETTINGS['alias']
    else:
        mongo_host = DevelopmentConfig.MONGODB_SETTINGS['host']
        mongo_alias = DevelopmentConfig.MONGODB_SETTINGS['alias']

    print(f"Connecting to MongoDB: {mongo_host}")

    if not mongo_host:
        raise ValueError("MongoDB host not found in environment variables")
    try:
        connect(host=mongo_host, alias=mongo_alias)
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)