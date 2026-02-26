from datetime import datetime, date

def parse_date_flexibly(date_str):
    """
    Safely parse multiple date formats into a Python date object.
    Returns None if parsing fails.
    """
    if not date_str:
        return None

    if isinstance(date_str, date):
        return date_str  # already a date object

    # Supported formats
    formats = [
        "%Y-%m-%d",      # 2023-01-01
        "%d/%m/%Y",      # 01/01/2023
        "%m/%d/%Y",      # 01/31/2023
        "%d-%m-%Y",      # 01-01-2023
        "%b %d %Y",      # Jan 01 2023
        "%B %d %Y",      # January 01 2023
        "%d %b %Y",      # 01 Jan 2023
        "%d %B %Y",      # 01 January 2023
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    # Optional: try using dateutil if available for super flexibility
    try:
        from dateutil import parser
        return parser.parse(date_str).date()
    except Exception:
        pass

    print(f"Unrecognized date format: {date_str}")
    return None

def safe_date(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None