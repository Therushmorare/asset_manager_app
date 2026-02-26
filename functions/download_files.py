from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash,send_file
from database import db
from datetime import datetime
import uuid
import csv
import io
from models.logs import UserLogs
"""
Download File
"""

#download logs
def download_logs():
    try:
        logs = UserLogs.query.all()
        if not logs:
            return {"message": "There Are No Logs"}, 404

        # Use in-memory file
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['DATE', 'USER ID', 'USER TYPE', 'ACTION'])

        # Write rows
        for log in logs:
            writer.writerow([log.created_at, log.user_id, log.applicant_type, log.action])

        output.seek(0)  # Move cursor back to start

        # Send as downloadable file
        return send_file(
            io.BytesIO(output.getvalue().encode()),  # Convert to bytes
            mimetype='text/csv',
            as_attachment=True,
            download_name='user_logs.csv'
        )

    except Exception as e:
        print(f"Log Error: {e}")
        return {"message": "Something went wrong, please try again later"}, 500

    finally:
        db.session.close()

#download files
#Since file link or url is already stored, use front end to download it.