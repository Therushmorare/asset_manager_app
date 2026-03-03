from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from database import db
from datetime import datetime
from model.logs import UserLogs
from model.admin import AdminUser
from model.asset_controller import AssetController
from model.asset_manager import AssetManager
from model.custodian import Custodian

"""
Capture all user logs throughout the app
"""

#user logs
def log_applicant_track(user_id, user_type, action_type):
    try:
        user = AdminUser.query.filter_by(admin_id=user_id).first() or \
                AssetController.query.filter_by(controller_id=user_id).first() or \
                AssetManager.query.filter_by(manager_id=user_id).first() or \
                Custodian.query.filter_by(user_id=user_id).first()

        if not user:
            raise ValueError(f"User {user_id} not found")

        save_data = UserLogs(
            user_id=user_id,
            applicant_type=user_type,
            action=action_type
        )

        db.session.add(save_data)
        db.session.commit()

        print("User action added to logs")

    except Exception as e:
        db.session.rollback()
        print(f"Log Error: {e}")