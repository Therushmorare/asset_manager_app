from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from flask_mail import Mail, Message
from mail_util import mail
from database import db
from flask import jsonify

"""
Send emails
"""

#verification email
def send_verification_email(email, verification_code):
    html_body = render_template('email_templates/code_verification.html',user_name=email,keyToken=verification_code)
    msg = Message('Verification', sender = 'bmaprojectgroup@gmail.com', recipients = [email])
    msg.html = html_body
    mail.send(msg)

#send credentials email
def send_credentials_email(email, password):
    html_body = render_template('email_templates/credentials.html',user_name=email, password=password)
    msg = Message('Verification', sender = 'bmaprojectgroup@gmail.com', recipients = [email])
    msg.html = html_body
    mail.send(msg)

def send_email(email, title, message):
    html_body = render_template('email_templates/alert.html',user_name=email, title=title, message=message)
    msg = Message('Application Status', sender = 'bmaprojectgroup@gmail.com', recipients = [email])
    msg.html = html_body
    mail.send(msg)

def send_rejection_email(email, first_name, last_name):
    html_body = render_template('email_templates/rejection.html',email=email, first_name=first_name, last_name=last_name)
    msg = Message('Application Status', sender = 'bmaprojectgroup@gmail.com', recipients = [email])
    msg.html = html_body
    mail.send(msg)

def send_interview_email(email, first_name, last_name, date, time, location, details, rescheduled=False):
    subject = "Interview Rescheduled" if rescheduled else "Interview Scheduled"
    
    html_body = render_template(
        'email_templates/interview.html',
        email=email,
        first_name=first_name,
        last_name=last_name,
        date=date,
        time=time,
        location=location,
        details=details
    )
    
    msg = Message(subject, sender='bmaprojectgroup@gmail.com', recipients=[email])
    msg.html = html_body
    mail.send(msg)


def send_offer_email(email, first_name, last_name, message):
    subject = "Job Offer"
    
    html_body = render_template(
        'email_templates/offer.html',
        email=email,
        first_name=first_name,
        last_name=last_name,
        message=message
    )
    
    msg = Message(subject, sender='bmaprojectgroup@gmail.com', recipients=[email])
    msg.html = html_body
    mail.send(msg)

def send_credentials(email, employee_number, first_name, last_name, password):
    subject = "Account Credentials"

    html_body = render_template(
        'email_templates/credentials.html',
        email=email,
        first_name=first_name,
        last_name=last_name,
        employee_number=employee_number,
        password=password
    )

    msg = Message(subject, sender='bmaprojectgroup@gmail.com', recipients=[email])
    msg.html = html_body
    mail.send(msg)
