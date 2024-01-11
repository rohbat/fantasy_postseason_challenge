from mongoengine import EmbeddedDocument, IntField, DecimalField

class PlayerStats(EmbeddedDocument):
    pass_yds = IntField()
    pass_td = IntField()
    rush_yds = IntField()
    rush_td = IntField()
    rec_yds = IntField()
    rec_td = IntField()
    rec = IntField()
    pass_int = IntField()
    fumbles = IntField()
    two_pt_conversions = IntField()
    score_normal = DecimalField(precision=2)
    score_half_ppr = DecimalField(precision=2)
    score_ppr = DecimalField(precision=2)
