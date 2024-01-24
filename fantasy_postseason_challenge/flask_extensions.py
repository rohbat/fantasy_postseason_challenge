from flask_login import LoginManager
from .classes.user import User

def initialize_extensions(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(username):
        return User.objects(username=username).first()