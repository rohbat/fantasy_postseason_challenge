import os

from flask import Flask

from .blueprints import register_blueprints
from .config import DevelopmentConfig, ProductionConfig
from .db import initialize_db, establish_db_connection
from .flask_extensions import initialize_extensions
from .utilities import setup_jinja_env

from flask_login import LoginManager

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if os.getenv('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    initialize_db(app)
    establish_db_connection()

    initialize_extensions(app)

    register_blueprints(app)

    setup_jinja_env(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
