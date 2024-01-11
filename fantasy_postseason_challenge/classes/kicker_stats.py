from mongoengine import EmbeddedDocument, IntField, DecimalField

class KickerStats(EmbeddedDocument):
    # FG made (0-39 yd)
    fg_0_39 = IntField()
    # FG made (40-49 yd)
    fg_40_49 = IntField()
    # FG made (50-59 yd)
    fg_50_59 = IntField()
    # FG made (60+ yd)
    fg_60 = IntField()
    # FG made
    fgm = IntField()
    # FG attempted
    fga = IntField()
    # PAT Made
    xpm = IntField()
    # PAT Attempted
    xpa = IntField()
    k_score_normal = DecimalField(precision=2)