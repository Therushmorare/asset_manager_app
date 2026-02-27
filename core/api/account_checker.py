"""
Check if user already exists
"""
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian

def check_user(email):
    try:
        users = AdminUser.query.filter_by(email=email).first() or \
                AssetController.query.filter_by(email=email).first() or \
                AssetManager.query.filter_by(email=email).first() or \
                Custodian.query.filter_by(email=email).first()
        
        if users:
            return {'message': 'User with that email already exists'}, 400
        
    except Exception as e:
        return {'message': 'Could not verify user'}, 500