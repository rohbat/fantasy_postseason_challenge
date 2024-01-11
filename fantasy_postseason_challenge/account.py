from .db import db
from .classes.league import League

class Account(db.Document):
    username = db.StringField(required=True, unique=True)
    display_name = db.StringField(required=True)
    password_hash = db.StringField(required=True)
    memberships = db.ListField(db.ReferenceField(League))

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username
    pass
