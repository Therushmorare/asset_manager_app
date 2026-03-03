import uuid
import random
from flask import current_app
from database import db
from datetime import datetime
from extensions import bcrypt
from functions.random_string import generate_random_string
from core.api.email_sender import send_credentials
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian
from core.api.account_checker import check_user
from functions.user_logs import log_applicant_track

"""
Add users
"""

VALID_USER_TYPES = ['ADMIN', 'ASSET_CONTROLLER', 'ASSET_MANAGER', 'CUSTODIAN']
VALID_ADMIN_ROLES = ['ADMIN', 'SUPERADMIN']

def add_user(email, first_name, last_name,
             department, role, phone_number,
             user_type, adder_id=None):

    try:
        # ---- Required Fields ----
        required = [email, first_name, last_name,
                    department, role, phone_number, user_type]

        if any(x is None for x in required):
            return {'message': 'Please add all fields'}, 400

        # ---- Validate user_type ----
        if user_type not in VALID_USER_TYPES:
            return {'message': 'Invalid user type'}, 400

        # ---- Check if user already exists ----
        existing = check_user(email)
        if existing:
            return {'message': 'User already exists'}, 400

        # ---- Permission Check ----
        if adder_id:
            admin = AdminUser.query.filter_by(admin_id=adder_id).first()
            if not admin:
                return {'message': 'You don’t have permission to perform this action!'}, 403

        # ---- Generate IDs & Password ----
        user_id = str(uuid.uuid4())
        current_year = datetime.now().year
        employee_number = f"EMP-{current_year}-{random.randint(1000, 9999)}"
        password = generate_random_string(8)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # ---- Create User Object ----
        if user_type == 'ADMIN':
            if role not in VALID_ADMIN_ROLES:
                return {'message': 'Invalid admin role'}, 400

            save_data = AdminUser(
                admin_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                employee_number=employee_number,
                department=department,
                role=role,
                phone_number=phone_number,
                password=hashed_password,
                mfa_required=True,
                is_active=True
            )

        elif user_type == 'ASSET_CONTROLLER':
            save_data = AssetController(
                controller_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                employee_number=employee_number,
                department=department,
                role='CONTROLLER',
                phone_number=phone_number,
                password=hashed_password,
                mfa_required=True,
                is_active=True
            )

        elif user_type == 'ASSET_MANAGER':
            save_data = AssetManager(
                manager_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                employee_number=employee_number,
                department=department,
                role='ASSET_MANAGER',
                phone_number=phone_number,
                password=hashed_password,
                mfa_required=True,
                is_active=True
            )

        else:  # CUSTODIAN
            save_data = Custodian(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                employee_number=employee_number,
                department=department,
                role='CUSTODIAN',
                phone_number=phone_number,
                password=hashed_password,
                mfa_required=True,
                is_active=True
            )

        db.session.add(save_data)
        db.session.commit()

        # ---- Send Email AFTER commit ----
        send_credentials(email, employee_number, first_name, last_name, password)

        # ---- Logs -------------------------
        if adder_id:
            #add logs
            log_applicant_track(adder_id, 'ADMIN', f'Added a new user with this ID:{user_id}')

        return {
            'message': 'User added successfully',
            'user_id': user_id
        }, 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Add User Error: {e}")
        return {'message': 'Something went wrong'}, 500