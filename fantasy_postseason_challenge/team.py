from .db import db

class Team(db.Document):
    QB = db.StringField(required=True)
    RB1 = db.StringField(required=True)
    RB2 = db.StringField(required=True)
    WR1 = db.StringField(required=True)
    WR2 = db.StringField(required=True)
    TE = db.StringField(required=True)
    FLEX = db.StringField(required=True)
    K = db.StringField(required=True)
    D_ST = db.StringField(required=True)