"""
Check if user already exists
"""
from models.admin import AdminUser
from models.asset_controller import AssetController
from models.asset_manager import AssetManager
from models.custodian import Custodian

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