from ..db import db
from .fantasy_team import FantasyTeam

class Member(db.EmbeddedDocument):
    team_name = db.StringField(required=True)
    account_id = db.ObjectIdField(required=True)
    week_1_team = db.ReferenceField(FantasyTeam)
    week_2_team = db.ReferenceField(FantasyTeam)
    week_3_team = db.ReferenceField(FantasyTeam)

class League(db.Document):
    league_name = db.StringField(required=True)
    commissioner_id = db.ObjectIdField(required=True)
    ruleset = db.StringField(required=True)
    member_list = db.ListField(db.EmbeddedDocumentField(Member))