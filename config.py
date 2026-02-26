import os
import stripe

# config.py
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASS_SLT')
    MAIL_SERVER='smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USERNAME = '97cc8d001@smtp-brevo.com'
    MAIL_PASSWORD = os.getenv('MAIL_SERVER_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    bucket_name = os.getenv('BUCKET_NAME')
    bucket_region = os.getenv('BUCKET_REGION')
    bucket_access_key = os.getenv('BUCKET_ACCESS_KEY')
    bucket_secret_key = os.getenv('BUCKET_SECRET_KEY')
    cloudfront = os.getenv('CLOUDFRONT')
    cloudfront_id = os.getenv('CLOUDFRONT_ID')
    databse_connection_string = os.getenv('POSTGRES_DB_CONNECTION')
    redis_connection = os.getenv('REDIS_DB')
    encryption_key = os.getenv('ACC_ENCRPTION_KEY')
    sms_username = os.getenv('SMS_USERNAME')
    sms_password =os.getenv('SMS_PASSWORD')
    google_key = os.getenv('GOOGLE_API')
    SENTRY_DSN = os.getenv('SENTRY')
    #removed NEWS_API