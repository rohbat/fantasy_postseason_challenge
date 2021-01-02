from .db import db

class Player(db.Document):
    name = db.StringField(required=True)
    team = db.StringField(required=True)
    position = db.StringField(required=True)
    
    week_1_avail = db.BooleanField(default=False)
    week_2_avail = db.BooleanField(default=False)
    week_3_avail = db.BooleanField(default=False)