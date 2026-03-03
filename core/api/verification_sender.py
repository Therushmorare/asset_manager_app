from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from itsdangerous import URLSafeTimedSerializer
import random
from flask import current_app
from redis_config import redis_client
from flask_mail import Mail, Message
from mail_util import mail
from database import db
from flask import jsonify
from .email_sender import send_verification_email
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian

"""
Send verification code and verify it
"""    
def send_verification_code(email):
    verification_code = random.randint(100000, 999999)
    redis_client.setex(f"otp:{email}", 300, str(verification_code))  # Store as string

    #send via email here instead of returning
    send_verification_email(email, verification_code)

def verify_token(user_email, token):
    # Look for user in both tables
    user = AdminUser.query.filter_by(email=user_email).first() or \
            AssetController.query.filter_by(email=user_email).first() or \
            AssetManager.query.filter_by(email=user_email).first() or \
            Custodian.query.filter_by(email=user_email).first()
    
    if not user:
        return {"message": "User not found"}, 404

    # Ensure token is a string
    user_otp = str(token)

    # Retrieve OTP from Redis
    stored_otp = redis_client.get(f"otp:{user_email}")
    if stored_otp:
        # Decode only if bytes
        if isinstance(stored_otp, bytes):
            stored_otp = stored_otp.decode("utf-8")

    # Compare OTPs
    if stored_otp and user_otp == stored_otp:
        user.confirmation_status = 'True'
        db.session.commit()
        redis_client.delete(f"otp:{user_email}")
        return {"message": "Verification Successful"}, 200

    return {"message": "Invalid or expired OTP"}, 401
