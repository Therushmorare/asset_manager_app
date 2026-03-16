from database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.String)
    asset_id = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    custodian = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    acquisition_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Numeric(12, 2), nullable=False)
    residual_value = db.Column(db.Numeric(12, 2), nullable=False)
    useful_life_years = db.Column(db.Integer, nullable=False)
    depreciation_method = db.Column(db.String(50), nullable=False)
    qr_code = db.Column(db.String, default='ACTIVE')
    status = db.Column(db.String)
    disposal_date = db.Column(db.String)
    disposal_value = db.Column(db.Double)
    gain_loss = db.Column(db.Double)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class DepreciationEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String)
    period = db.Column(db.String)  # e.g., '2026-02'
    depreciation_amount = db.Column(db.Float)
    book_value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())