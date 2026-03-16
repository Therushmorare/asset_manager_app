from database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date


class AssetQRCodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=True)
    url = db.Column(db.String)
    status = db.Column(db.String)
