from ..db import db
from ..config import get_db_alias
from .league import League

class User(db.Document):
    username = db.StringField(required=True, unique=True)
    display_name = db.StringField(required=True)
    password_hash = db.StringField(required=True)
    memberships = db.ListField(db.ReferenceField('League'))

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Users'  # Collection name
    }
