from ..config import get_db_alias
from mongoengine import Document, StringField, IntField

class Player(Document):
    name = StringField(required=True)
    team = StringField(required=True)
    position = StringField(required=True)
    display_name = StringField(required=True)
    games_started = IntField(required=True, default=0)
    
    def get_display_name(self):
        return '[' + self.team + '] ' + self.name

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Players'  # Collection name
    }
    