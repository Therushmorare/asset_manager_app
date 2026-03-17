import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_model import MFA_Code


def verify_mfa_code(user_id, code):
    """
    Check if the MFA code is valid and return JSON-compatible response
    """
    try:
        # Look for unverified MFA record
        mfa_record = MFA_Code.query.filter_by(
            user_id=user_id,
            code=code,
            verified=False
        ).first()

        if not mfa_record:
            return {"success": False, "message": "Invalid code"}, 401

        # Check expiration
        expires_aware = mfa_record.expires_at.replace(tzinfo=timezone.utc)
        if expires_aware < datetime.now(timezone.utc):
            return {"success": False, "message": "Code expired"}, 401

        # Mark code as verified
        mfa_record.verified = True
        db.session.commit()

        return {
            "success": True,
            "message": "Code verified successfully"
        }, 200

    except Exception as e:
        db.session.rollback()
        print("ERROR verify_mfa_code:", str(e))
        return {"success": False, "message": "Server error"}, 500