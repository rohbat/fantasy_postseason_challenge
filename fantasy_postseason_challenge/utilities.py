from .config import GAMES
from datetime import datetime
from dateutil import tz

def is_round_locked(round_name):
    current_time = datetime.now(tz.UTC)
    round_start_time = GAMES.get(round_name)['start_time']
    return current_time > round_start_time if round_start_time else False