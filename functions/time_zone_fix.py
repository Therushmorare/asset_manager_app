from datetime import datetime
from zoneinfo import ZoneInfo


def local_now():
    return datetime.now(ZoneInfo("Africa/Johannesburg"))