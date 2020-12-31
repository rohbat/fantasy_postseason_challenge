import os
from .db import initialize_db

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
        print(app.config['MONGODB_HOST'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    initialize_db(app)

    with app.app_context():
        from . import routes
        print(app.config['MONGODB_HOST'])
        return app
