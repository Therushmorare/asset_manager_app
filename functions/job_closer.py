from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from database import db
from datetime import datetime, timezone
from models.job_application import JobApplication
from models.job_post import JobPost
from functions.celery_worker import celery_ext

"""
Automatically Close Job Posts
After Thrashhold is reached
"""

#job closer by number of applicants
@celery_ext.celery.task
def job_closer(job_id):
    try:
        # Get job post
        post = JobPost.query.filter_by(job_id=job_id).first()
        if not post:
            print("Job Post No Longer Available")
            return None

        # Count applications
        total_applied = JobApplication.query.filter_by(job_id=job_id).count()
        print(f"Total Applications: {total_applied}, Job Quantity: {post.quantity}")

        # Convert datetimes to timezone-aware (UTC)
        now = datetime.now(timezone.utc)
        closing_date = post.closing_date
        if closing_date.tzinfo is None:
            closing_date = closing_date.replace(tzinfo=timezone.utc)

        # --- Closing logic ---
        if total_applied >= int(post.quantity):
            post.status = 'CLOSED'
            db.session.commit()
            print("Job Post closed (application limit reached)")
            return "CLOSED"

        elif now > closing_date:
            post.status = 'CLOSED'
            db.session.commit()
            print("Job Post closed (closing date passed)")
            return "CLOSED"

        else:
            print("Job Post still open")
            return "OPEN"

    except Exception as e:
        db.session.rollback()
        print(f"Job Closer Error: {e}")
        return None

    finally:
        db.session.close()