import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import MFA_Code


def verify_mfa_code(user_id, code):
    """Check if the MFA code is valid"""
    mfa_record = MFA_Code.query.filter_by(user_id=user_id, code=code, verified=False).first()
    if not mfa_record:
        return False, "Invalid code"

    expires_aware = mfa_record.expires_at.replace(tzinfo=timezone.utc)

    if expires_aware < datetime.now(timezone.utc):
        return False, "Code expired"

    mfa_record.verified = True
    db.session.commit()
    return True, "Code verified successfully"
