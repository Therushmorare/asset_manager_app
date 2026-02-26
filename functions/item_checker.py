from datetime import datetime, timedelta, timezone

last_checked = {}

def should_check(item_id):
    now = datetime.now(timezone.utc)  # current UTC time
    if item_id not in last_checked or (now - last_checked[item_id]) > timedelta(minutes=10):
        last_checked[item_id] = now
        return True
    return False