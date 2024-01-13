import os
from .db import initialize_db
from .config import DevelopmentConfig
from .classes.user import User

from flask import Flask, request, redirect
from flask_login import LoginManager

from urllib.parse import urlparse, urlunparse

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    app.config.from_object(DevelopmentConfig)

    initialize_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(username):
        return User.objects(username=username).first()

    @app.before_request
    def redirect_subdomains():
        """Redirect non-www and www requests to football.<domain>"""
        urlparts = urlparse(request.url)
        if urlparts.netloc == 'fantasypostseasonchallenge.com' or urlparts.netloc == 'www.fantasypostseasonchallenge.com':
            urlparts = urlparts._replace(netloc='football.fantasypostseasonchallenge.com')
            return redirect(urlunparse(urlparts), code=301)
        
    from . import auth, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)

    app.jinja_env.globals.update(
        zip=zip,
        enumerate=enumerate,
        len=len,
        list=list,
        reversed=reversed
    )

    # EDIT WEEK VALUE HERE
    app.WEEK = 3

    return app
