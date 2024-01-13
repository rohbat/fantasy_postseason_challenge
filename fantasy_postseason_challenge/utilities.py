from .config import PLAYOFF_START_TIMES
from datetime import datetime
from dateutil import tz

def is_round_locked(round_name):
    current_time = datetime.now(tz.UTC)
    round_start_time = PLAYOFF_START_TIMES.get(round_name)
    return current_time > round_start_time if round_start_time else False