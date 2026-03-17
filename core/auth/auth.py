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
User login & Signup
"""

types = ["admin", "asset_manager", "asset_controller", "custodian"]
MAX_ATTEMPTS = 5 #for login purposes

        
#login function
def signin_applicants(email, password, user_type):
    try:
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        if session['login_attempts'] >= MAX_ATTEMPTS:
            return {"message": "Too many login attempts, your account will be locked for an hour. Please try again later."}, 401

        # Get applicant account
        user = AdminUser.query.filter_by(email=email).first() or \
                AssetController.query.filter_by(email=email).first() or \
                AssetManager.query.filter_by(email=email).first() or \
                Custodian.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            session['login_attempts'] += 1
            return {"message": "User not found"}, 404

        # Verify password
        if not bcrypt.check_password_hash(user.password, password):
            session['login_attempts'] += 1
            return {"message": "Password is incorrect"}, 401

        # Verify account confirmation
        if str(user.confirmation_status) != "True":
            return {"message": "Please verify your account before logging in"}, 401

        # Reset login attempts
        session.pop('login_attempts', None)

        #mfa code send
        if isinstance(user, AdminUser):
            user_type = "admin"
            user_id = user.admin_id
        elif isinstance(user, AssetManager):
            user_type = "asset_manager"
            user_id = user.manager_id
        elif isinstance(user, AssetController):
            user_type = "asset_controller"
            user_id = user.controller_id
        else:
            user_type = "custodian"
            user_id = user.user_id

        # Generate MFA
        mfa_code = save_mfa_code(user_id, user_type)
        user_email = getattr(user, "email", email)
        if user_email:
            send_mfa_email(user_email, user_type, mfa_code)

        # Perform login + create JWT
        login_user(user)
        access_token = create_access_token(
            identity=str(user.applicant_id),  # must be a string
            additional_claims={"role": f"{user_type}_applicant"},
            expires_delta=timedelta(hours=1)
        )

        return {
            "message": "User logged in successfully",
            "email": email,
            "user_type": user_type,
            "user_id": user.applicant_id,
            "access_token": access_token
        }, 200

    except Exception as e:
        print(f"There was an error during signin: {e}")
        return {"message": "Something went wrong"}, 500
