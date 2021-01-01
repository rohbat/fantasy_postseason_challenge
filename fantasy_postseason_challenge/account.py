from .db import db

class User(db.Document):
    username = db.StringField(required=True)
    password_hash = db.StringField(required=True)
    memberships = db.ListField()

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username
