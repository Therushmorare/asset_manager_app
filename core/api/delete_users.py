import uuid
import random
from flask import current_app
from database import db
from datetime import datetime
from extensions import bcrypt
from functions.random_string import generate_random_string
from core.api.email_sender import send_credentials
from models.admin import AdminUser
from models.asset_controller import AssetController
from models.asset_manager import AssetManager
from models.custodian import Custodian
from models.asset import Asset
from core.api.account_checker import check_user
from functions.user_logs import log_applicant_track


def delete_user(requester_id, user_id, user_type):
    try:
        # ---- Permission Check ----
        requester = AdminUser.query.filter_by(admin_id=requester_id).first()
        if not requester:
            return {'message': 'Only admins can delete users'}, 403

        # ---- Prevent Self Deletion ----
        if requester_id == user_id:
            return {'message': 'You cannot delete your own account'}, 400

        # ---- Fetch Target User ----
        user = None

        if user_type == "ADMIN":
            user = AdminUser.query.filter_by(admin_id=user_id).first()
        elif user_type == "ASSET_MANAGER":
            user = AssetManager.query.filter_by(manager_id=user_id).first()
        elif user_type == "ASSET_CONTROLLER":
            user = AssetController.query.filter_by(controller_id=user_id).first()
        elif user_type == "CUSTODIAN":
            user = Custodian.query.filter_by(user_id=user_id).first()
        else:
            return {'message': 'Invalid user type'}, 400

        if not user:
            return {'message': 'User not found'}, 404

        # ---- Prevent Deleting SUPERADMIN ----
        if hasattr(user, "role") and user.role == "SUPERADMIN":
            if requester.role != "SUPERADMIN":
                return {'message': 'Only SUPERADMIN can delete another SUPERADMIN'}, 403

        # ---- Optional: Prevent deleting user with active assets ----
        if user_type == "CUSTODIAN":
            active_assets = Asset.query.filter_by(
                custodian=user_id,
                status="ACTIVE"
            ).count()

            if active_assets > 0:
                return {
                    'message': 'Cannot delete custodian with active assigned assets'
                }, 400

        # ---- Soft Delete ----
        user.is_active = False

        db.session.commit()

        log_applicant_track(
            requester_id,
            "ADMIN",
            f"User {requester_id} deactivated user {user_id}"
        )

        return {'message': 'User deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete User Error: {e}")
        return {'message': 'Something went wrong'}, 500