from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

"""
Asset Control User
"""

class AssetController(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    controller_id = db.Column(db.String)
    email = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    employee_number = db.Column(db.String)
    department = db.Column(db.String)
    role = db.Column(db.String)
    phone_number = db.Column(db.String)
    password = db.Column(db.String)
    mfa_required = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(DateTime(timezone=True), default=local_now)