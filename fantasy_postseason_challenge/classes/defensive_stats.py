from mongoengine import EmbeddedDocument, IntField, DecimalField

class DefensiveStats(EmbeddedDocument):
    # Points allowed
    points_allowed = IntField()
    # Defense sacks
    sacks = IntField()
    # Defense interceptions
    def_int = IntField()
    # Defensive ints for TDs
    def_int_td = IntField()
    # Defense fumble recoveries
    fumbles_rec = IntField()
    # Defense fumbles recovered for TDs
    fumbles_rec_td = IntField()
    # Defense safeties (Not currently scraped)
    safeties = IntField()
    # Special teams tds (Not currently scraped)
    st_tds = IntField()
    # Special teams blocked kick (Not currently scraped)
    st_blocked_kicks = IntField()
    # Special teams fumble recovery (Not currently scraped)
    st_fumble_recoveries = IntField()
    d_st_score_normal = DecimalField(precision=2)