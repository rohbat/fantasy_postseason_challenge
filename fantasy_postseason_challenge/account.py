from .db import db

class Account(db.Document):
    username = db.StringField(required=True)
    password_hash = db.StringField(required=True)
    leagues = db.ListField()