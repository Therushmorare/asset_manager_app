from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from database import db
from datetime import datetime
from models.logs import UserLogs, AppUserLogs
from models.applicant import ExternalApplicant, InternalApplicant
from models.hr_account import Recruiter
from models.admin_user import AdminUser
"""
Capture all user logs throughout the app
"""

#user logs
def log_applicant_track(user_id, user_type, action_type):
    try:
        user = (
            ExternalApplicant.query.filter_by(applicant_id=user_id).first() or
            InternalApplicant.query.filter_by(applicant_id=user_id).first() or
            Recruiter.query.filter_by(employee_id=user_id).first() or
            AdminUser.query.filter_by(admin_id=user_id).first()
        )

        if not user:
            raise ValueError(f"User {user_id} not found")

        save_data = AppUserLogs(
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