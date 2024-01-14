from ..config import get_db_alias
from ..db import db
from .lineup import Lineup

class Member(db.EmbeddedDocument):
    team_name = db.StringField(required=True)
    account = db.ReferenceField('User', required=True)  # Updated to reference User
    wildcard_team = db.ReferenceField(Lineup)
    divisional_team = db.ReferenceField(Lineup)
    championship_team = db.ReferenceField(Lineup)

    def __repr__(self):
        return (f"Member(team_name={self.team_name}, "
                f"account={self.account}, "
                f"wildcard_team={self.wildcard_team}, "
                f"divisional_team={self.divisional_team}, "
                f"championship_team={self.championship_team})")

class League(db.Document):
    league_name = db.StringField(required=True)
    commissioner = db.ReferenceField('User', required=True)  # Updated to reference User
    ruleset = db.StringField(required=True)
    member_list = db.ListField(db.EmbeddedDocumentField(Member))

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Leagues'  # Collection name
    }

    def __repr__(self):
        return f"Team(...)"
