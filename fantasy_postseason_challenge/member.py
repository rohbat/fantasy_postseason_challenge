from .db import db
from .fantasy_team import FantasyTeam

class Member(db.Document):
    team_name = db.StringField(required=True)
    account_id = db.ObjectIdField(required=True)
    league_name = db.StringField(required=True)
    league_id = db.ObjectIdField(required=True)
    week_1_team = db.ReferenceField(FantasyTeam)