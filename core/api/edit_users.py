import uuid
import random
from flask import current_app
from database import db, datetime
from extensions import bcrypt
from functions.random_string import generate_random_string
from api.email_sender import send_credentials
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian
from api.account_checker import check_user
from functions.user_logs import log_applicant_track

"""
Edit users
"""

def edit_user(editor_id, user_id, user_type, **updates):
    """
    editor_id: person performing the edit
    user_id: user being edited
    user_type: ADMIN | ASSET_MANAGER | ASSET_CONTROLLER | CUSTODIAN
    updates: fields to update (email, department, role, etc.)
    """

    try:
        # ---- Permission Check (only admins can edit) ----
        editor = AdminUser.query.filter_by(admin_id=editor_id).first()
        if not editor:
            return {'message': 'You do not have permission to perform this action'}, 403

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

        # ---- Prevent Superadmin Editing (optional safety) ----
        if hasattr(user, "role") and user.role == "SUPERADMIN":
            if editor.role != "SUPERADMIN":
                return {'message': 'Only SUPERADMIN can edit another SUPERADMIN'}, 403

        # ---- Update Allowed Fields Only ----
        allowed_fields = [
            "email", "first_name", "last_name",
            "department", "phone_number",
            "role", "is_active", "mfa_required"
        ]

        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        db.session.commit()

        #logs here
        log_applicant_track(editor_id, 'ADMIN', f'Edited account/profile details of :{user_id}')

        return {'message': 'User updated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Edit User Error: {e}")
        return {'message': 'Something went wrong'}, 500