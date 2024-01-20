from ..config import get_db_alias
from ..db import db
from mongoengine import DecimalField, StringField, MapField, IntField, URLField

class Scores(db.EmbeddedDocument):
    # playoff_round = StringField(required=True)
    standard = DecimalField(precision=2)
    half_ppr = DecimalField(precision=2)
    ppr = DecimalField(precision=2)

class CustomURLField(URLField):
    def validate(self, value):
        # Allow empty strings
        if value == '':
            return

        # Use the parent class's validation for non-empty strings
        super().validate(value)

class Player(db.Document):
    name = StringField(required=True)
    team = StringField(required=True)
    position = StringField(required=True)
    display_name = StringField(required=True)
    games_started = IntField(required=True, default=0)
    playoff_scores = MapField(db.EmbeddedDocumentField(Scores))
    headshot_url = CustomURLField()
    
    def get_display_name(self):
        return '[' + self.team + '] ' + self.name

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Players'  # Collection name
    }
    