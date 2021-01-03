from .db import db
from .member import Member

class League(db.Document):
    league_name = db.StringField(required=True)
    commissioner_id = db.ObjectIdField(required=True)
    ruleset = db.StringField(required=True)
    member_id_list = db.ListField(db.EmbeddedDocumentField(Member))