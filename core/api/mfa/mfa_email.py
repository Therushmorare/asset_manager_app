from flask_mail import Mail, Message
from mail_util import mail
from flask import render_template
from functions.celery_worker import celery_ext

@celery_ext.celery.task
def send_mfa_email(email, user_type, code):
    subject = f"{user_type.capitalize()} MFA Verification Code"
    html_body = render_template('email_templates/mfa.html', keyToken=code, user_name=email)
    msg = Message(subject, sender='bmaprojectgroup@gmail.com', recipients=[email])
    msg.html = html_body
    mail.send(msg)