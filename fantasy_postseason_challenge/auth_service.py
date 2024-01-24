from werkzeug.security import check_password_hash, generate_password_hash
from .classes.user import User
from flask_login import login_user

def register_user(username, password, display_name):
    if not (username and password and display_name):
        return False, "Username, password, and display name are required."

    if User.objects(username=username).first():
        return False, f"Username: \"{username}\" already exists."

    new_user = User(username=username, password_hash=generate_password_hash(password), display_name=display_name)
    new_user.save()
    login_user(new_user)
    return True, "Registration successful."

def authenticate_user(username, password):
    if not (username and password):
        return None, "Username and password are required."

    user = User.objects(username=username).first()
    if not user:
        return None, f"Username: \"{username}\" not found."
    elif not check_password_hash(user.password_hash, password):
        return None, "Incorrect password."

    login_user(user)
    return user, "Authentication successful."