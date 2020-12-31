import os
from .db import initialize_db
from .account import User

from flask import Flask
from flask_login import LoginManager

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    initialize_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(username):
        return User.objects(username=username).first()

    with app.app_context():
        from . import routes
        return app
