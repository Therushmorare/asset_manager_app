from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from database import db
from functions.user_logs import log_applicant_track
import uuid
from models.notifications import ApplicantNotifications

"""
User notifications
"""

def applicant_notifications(sender, receiver, title, description):
    try:
        save_notification = ApplicantNotifications(
            sender=sender,
            receiver=receiver,
            title=title,
            description=description
        )

        db.session.add(save_notification)
        db.session.commit()

        print(
            f"Notification added successfully"
        )

        return None

    except Exception as e:
        db.session.rollback()
        print(f"Notification Error: {e}")
        return jsonify({
            "message": "Something went wrong, please try again later",
        }), 500

    finally:
        db.session.close()
