from database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class AssetVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String)
    custodian_id = db.Column(db.String)
    verification_id = db.Column(db.String)
    status = db.Column(db.String)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())