from database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class DisposalLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String)
    disposal_id = db.Column(db.String)
    manager_id = db.Column(db.String)
    reason = db.Column(db.Text)
    method = db.Column(db.String)
    date = db.Column(db.String)
    proceeds = db.Column(db.Double)
    net_book_value = db.Column(db.Double)
    gain_loss = db.Column(db.Double)
    url = db.Column(db.String)
    status = db.Column(db.String)
    approved_by = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    approved_at = db.Column(db.String)