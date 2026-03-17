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
# from your_sage_integration import check_user_in_sage  # placeholder

"""
Re send MFA
"""

def resend_mfa(email, user_type):
    try:
        if email is None:
            return {'message': 'A valid email must be provided'}, 400
        
        if not user_type:
            return {'message': 'A valid user type must be provided'}, 400
        
        # Get applicant account
        user = AdminUser.query.filter_by(email=email).first() or \
                AssetController.query.filter_by(email=email).first() or \
                AssetManager.query.filter_by(email=email).first() or \
                Custodian.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            return {"message": "User not found"}, 404
        
        mfa_code = save_mfa_code(user.id, user_type)
        user_email = getattr(user, "email", email)

        if user_email:
            send_mfa_email(user_email, user_type, mfa_code)

        return {'message': f'MFA code has been re-sent to your email: {email}'}, 200
    
    except Exception as e:
        print(f"MFA RESEND ERROR:{e}")
        return {'message': 'Something went wrong'}, 500