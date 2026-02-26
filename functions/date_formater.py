from datetime import datetime, date

def format_date(value):
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    try:
        # Try to parse if it's a string (handle multiple formats)
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        return value  # fallback — it's already in usable format