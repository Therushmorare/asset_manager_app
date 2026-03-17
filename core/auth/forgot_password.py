from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from itsdangerous import URLSafeTimedSerializer
from database import db
import datetime
import uuid
from extensions import bcrypt
from core.api.verification_sender import *
import os
from flask_mail import Mail, Message
from mail_util import mail
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from core.api.email_sender import *
from models.admin import AdminUser
from models.asset_manager import AssetManager
from models.asset_controller import AssetController
from models.custodian import Custodian
import secrets
from flask_jwt_extended import create_access_token
from datetime import timedelta
from core.mfa.mfa_code_generation import save_mfa_code
from core.mfa.mfa_email import send_mfa_email
from core.api.mfa.verify_mfa_code import verify_mfa_code
from functions.random_string import generate_random_string
from core.api.email_sender import send_credentials
# from your_sage_integration import check_user_in_sage  # placeholder

"""
Forgot password
"""

def forgot_password(email):
    try:
        if not email:
            return {'message': 'Please enter email'}, 400
        
        # Get applicant account
        user = AdminUser.query.filter_by(email=email).first() or \
                AssetController.query.filter_by(email=email).first() or \
                AssetManager.query.filter_by(email=email).first() or \
                Custodian.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            return {"message": "User not found"}, 404
        
        #send verification code
        mfa_code = save_mfa_code(user.id, 'Auth User')
        user_email = getattr(user, "email", email)

        if user_email:
            send_mfa_email(user_email, 'Auth User', mfa_code)

        return {'message': f'MFA code has been re-sent to your email: {email}'}, 200
    
    except Exception as e:
        print(f'Forgot Error:{e}')
        return {'message': 'Something went wrong'}, 500

def verify_to_password(email, token):
    if not token:
        return {'message': f'Enter token sent to {email}'}, 400

    user = (
        AdminUser.query.filter_by(email=email).first() or
        AssetController.query.filter_by(email=email).first() or
        AssetManager.query.filter_by(email=email).first() or
        Custodian.query.filter_by(email=email).first()
    )

    if not user:
        return {"message": "User not found"}, 404

    try:
        user_id = getattr(user, 'admin_id', None) or \
                  getattr(user, 'manager_id', None) or \
                  getattr(user, 'controller_id', None) or \
                  getattr(user, 'user_id', None)

        verify_mfa_code(user_id, token)

        new_pass = generate_random_string(8)
        user.password = bcrypt.generate_password_hash(new_pass).decode('utf-8')

        db.session.commit()

        send_credentials(
            user.email,
            user.employee_number,
            user.first_name,
            user.last_name,
            new_pass
        )

        return {'message': 'Password reset successful'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Error: {e}')
        return {'message': 'Verification failed'}, 500