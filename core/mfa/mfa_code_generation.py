import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import MFA_Code

def generate_mfa_code(length=6):
    """Generate numeric MFA code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def save_mfa_code(user_id, user_type, code=None, ttl_minutes=10):
    """Save MFA code in DB with expiry"""
    if not code:
        code = generate_mfa_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    
    mfa = MFA_Code(
        user_id=user_id,
        user_type=user_type,
        code=code,
        expires_at=expires_at
    )
    db.session.add(mfa)
    db.session.commit()
    return code