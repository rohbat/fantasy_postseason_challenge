from ..config import get_db_alias
from .lineup import Lineup

class Member(db.EmbeddedDocument):
    team_name = db.StringField(required=True)
    account = db.ReferenceField('User', required=True)  # Updated to reference User
    wildcard_team = db.ReferenceField(Lineup)
    divisional_team = db.ReferenceField(Lineup)
    championship_team = db.ReferenceField(Lineup)

class League(db.Document):
    league_name = db.StringField(required=True)
    commissioner = db.ReferenceField('User', required=True)  # Updated to reference User
    ruleset = db.StringField(required=True)
    member_list = db.ListField(db.EmbeddedDocumentField(Member))

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Leagues'  # Collection name
    }
