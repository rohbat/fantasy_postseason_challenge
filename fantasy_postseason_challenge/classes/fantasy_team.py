from ..db import db

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
    two_pt_conversions = db.IntField()

    score_normal = db.DecimalField(precision=2)
    score_half_ppr = db.DecimalField(precision=2)
    score_ppr = db.DecimalField(precision=2)

    # Defensive stats
    # Points allowed
    points_allowed = db.IntField()
    # Defense sacks
    sacks = db.IntField()
    # Defense interceptions
    def_int = db.IntField()
    # Defensive ints for TDs
    def_int_td = db.IntField()
    # Defense fumble recoveries
    fumbles_rec = db.IntField()
    # Defense fumbles recovered for TDs
    fumbles_rec_td = db.IntField()
    # Defense safeties (Not currently scraped)
    safeties = db.IntField()
    # Special teams tds (Not currently scraped)
    st_tds = db.IntField()
    # Special teams blocked kick (Not currently scraped)
    st_blocked_kicks = db.IntField()
    # Special teams fumble recovery (Not currently scraped)
    st_fumble_recoveries = db.IntField()
    
    d_st_score_normal = db.DecimalField(precision=2)

    # Kicker Stats
    # FG made (0-39 yd)
    fg_0_39 = db.IntField()
    # FG made (40-49 yd)
    fg_40_49 = db.IntField()
    # FG made (50-59 yd)
    fg_50_59 = db.IntField()
    # FG made (60+ yd)
    fg_60 = db.IntField()
    # FG made
    fgm = db.IntField()
    # FG attempted
    fga = db.IntField()
    # PAT Made
    xpm = db.IntField()
    # PAT Attempted
    xpa = db.IntField()
    
    k_score_normal = db.DecimalField(precision=2)


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