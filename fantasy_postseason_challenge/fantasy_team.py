from .db import db

class PlayerStats(db.EmbeddedDocument):
    pass_yds = db.IntField()
    pass_td = db.IntField()
    rush_yds = db.IntField()
    rush_td = db.IntField()
    rec_yds = db.IntField()
    rec_td = db.IntField()
    rec = db.IntField()
    pass_int = db.IntField()
    fumbles = db.IntField()
    score_normal = db.DecimalField(required=True, default=0, precision=2)
    score_half_ppr = db.DecimalField(required=True, default=0, precision=2)
    score_ppr = db.DecimalField(required=True, default=0, precision=2)

class Player(db.Document):
    name = db.StringField(required=True)
    team = db.StringField(required=True)
    position = db.StringField(required=True)
    display_name = db.StringField(required=True, default=f'[{team}] {name}')
    games_started = db.IntField(requred=True, default=0)

    week_1_avail = db.BooleanField(default=False)
    week_2_avail = db.BooleanField(default=False)
    week_3_avail = db.BooleanField(default=False)

    week_1_stats = db.EmbeddedDocumentField(PlayerStats)
    week_2_stats = db.EmbeddedDocumentField(PlayerStats)
    week_3_stats = db.EmbeddedDocumentField(PlayerStats)

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