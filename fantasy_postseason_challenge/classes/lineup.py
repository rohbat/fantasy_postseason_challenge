from ..db import db
from ..config import get_db_alias
from .player import Player

class Lineup(db.Document):
    QB = db.ReferenceField(Player)
    RB1 = db.ReferenceField(Player)
    RB2 = db.ReferenceField(Player)
    WR1 = db.ReferenceField(Player)
    WR2 = db.ReferenceField(Player)
    TE = db.ReferenceField(Player)
    FLEX = db.ReferenceField(Player)
    K = db.ReferenceField(Player)
    D_ST = db.ReferenceField(Player)

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Lineups'  # Collection name
    }