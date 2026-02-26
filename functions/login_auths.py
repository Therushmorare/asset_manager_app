import logging
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from models.applicant import ExternalApplicant, InternalApplicant
from models.hr_account import Recruiter
from models.admin_user import AdminUser

logger = logging.getLogger(__name__)
login_manager = LoginManager()
login_manager.login_view = 'login'  # endpoint name for login

# ---------------------------
# User loader
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    logger.info(f'Loading user with ID: {user_id}')
    
    # Try loading from ExternalApplicant
    user = ExternalApplicant.query.get(user_id)
    if user:
        user.user_type = 'External'
        logger.info(f'External User loaded: {user.email}')
        return user
    
    # Try loading from InternalApplicant
    user = InternalApplicant.query.get(user_id)
    if user:
        user.user_type = 'Internal'
        logger.info(f'Internal User loaded: {user.email}')
        return user
    
    #Try loading Recruiter
    user = Recruiter.query.get(user_id)
    if user:
        user.user_type = 'HR'
        logger.info(f'Recruiter User loaded: {user.email}')
        return user

    #Try loading from AdminUSer
    user = AdminUser.query.get(user_id)
    if user:
        user.user_type = 'Admin'
        logger.info(f'Recruiter User loaded: {user.email}')
        return user

    logger.warning(f'User not found: {user_id}')
    return None

# ---------------------------
# Unauthorized handler
# ---------------------------
@login_manager.unauthorized_handler
def unauthorized():
    logger.info(f'Unauthorized access attempt to {request.url}')
    session['next'] = request.url
    # Redirect to login page
    return redirect(url_for('login'))
