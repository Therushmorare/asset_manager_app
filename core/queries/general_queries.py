#!/usr/bin/python3
from redis_config import redis_client
from flask import jsonify, request
from sqlalchemy import desc
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from math import ceil
from functions.celery_worker import celery_ext
from functions.date_formater import format_date
from functions.date_parser import parse_date_flexibly, safe_date
from database import db
from models.asset import Asset, DepreciationEntry

#get asset data
def get_assets():
    try:
        assets = Asset.query.all()

        if not assets:
            return {'message': 'Assets dont exist'}, 404
        
        result = [
            {
                'added_by': asset.added_by,
                'asset_id': asset.asset_id,
                'name': asset.name,
                'description': asset.description,
                'category': asset.category,
                'sub_category': asset.sub_category,
                'department': asset.department,
                'custodian': asset.custodian,
                'location': asset.location,
                'acquisition_date': asset.acquisition_date,
                'cost': asset.cost,
                'residual_value': asset.residual_value,
                'useful_life_years': asset.useful_life_years,
                'depreciation_method': asset.depreciation_method,
                'qr_code': asset.qr_code,
                'status': asset.status,
                'disposal_date': asset.disposal_date,
                'disposal_value': asset.disposal_value,
                'gain_loss': asset.gain_loss,
                'created_at': asset.created_at,
                'updated_at': asset.updated_at
            }
            for asset in assets
        ]
        return result, 200
    
    except Exception as e:
        print(f"Get all assets error:{e}")
        return {'message': 'Something went wrong'}, 500