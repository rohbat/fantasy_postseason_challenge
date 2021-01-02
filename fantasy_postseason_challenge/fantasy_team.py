from .db import db

class Player(db.Document):
    name = db.StringField(required=True)
    team = db.StringField(required=True)
    position = db.StringField(required=True)
    display_name = db.StringField(required=True, default=self.get_display_name())

    week_1_avail = db.BooleanField(default=False)
    week_2_avail = db.BooleanField(default=False)
    week_3_avail = db.BooleanField(default=False)

    def get_display_name(self):
        return '[' + team + '] ' + name 

class FantasyTeam(db.Document):
    QB = db.ReferenceField(Player)
    RB1 = db.ReferenceField(Player)
    RB2 = db.ReferenceField(Player)
    WR1 = db.ReferenceField(Player)
    WR2 = db.ReferenceField(Player)
    TE = db.ReferenceField(Player)
    FLEX = db.ReferenceField(Player)
    K = db.ReferenceField(Player)
    D_ST = db.ReferenceField(Player)