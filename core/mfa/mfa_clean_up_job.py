import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import MFA_Code

def cleanup_expired_mfa_codes():
    expired = MFA_Code.query.filter(MFA_Code.expires_at < datetime.now(timezone.utc)).all()
    for code in expired:
        db.session.delete(code)
    db.session.commit()
