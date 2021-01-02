from .db import db

class Member(db.Document):
    team_name = db.StringField(required=True)
    account_id = db.ObjectIdField(required=True)
    league_name = db.StringField(required=True)
    league_id = db.ObjectIdField(required=True)