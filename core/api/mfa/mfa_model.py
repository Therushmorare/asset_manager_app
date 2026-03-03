from datetime import datetime, timedelta, timezone
from database import db

class MFA_Code(db.Model):
    __tablename__ = 'mfa_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'admin', 'applicant', etc.
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, default=False)
