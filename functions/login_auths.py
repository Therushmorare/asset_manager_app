import logging
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian

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
    user = AssetController.query.get(user_id)
    if user:
        user.user_type = 'Controller'
        logger.info(f'Asset Controller User loaded: {user.email}')
        return user
    
    # Try loading from InternalApplicant
    user = AssetManager.query.get(user_id)
    if user:
        user.user_type = 'Manager'
        logger.info(f'Asset Manager User loaded: {user.email}')
        return user
    
    #Try loading Recruiter
    user = Custodian.query.get(user_id)
    if user:
        user.user_type = 'Custodian'
        logger.info(f'Custodian User loaded: {user.email}')
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
