# app.py
import os, logging, boto3
from flask import Flask, request, jsonify, session
from redis import Redis
from dotenv import load_dotenv
from flask_restx import Api
from functools import wraps

from config import Config
from extensions import db, bcrypt, mail, cache, limiter, session_ext, babel, jwt
from functions.celery_worker import celery_ext
from functions.bug_logger import init_sentry, init_email_fallback
from mail_util import init_mail
from core.auth import *
from functions.login_auths import login_manager  # import the login_manager instance
from functions.error_handlers import register_error_handlers
from flask_cors import CORS

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

# === ADD THIS SECTION ===
    # Allow cross-origin requests from your frontend (http://127.0.0.1:5500)
    #Allow cross-origin request from your production frontend (https://appbma.netlify.app)
    # or use '*' for full open access during dev.
    CORS(app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://127.0.0.1:5500",
                    "http://localhost:3000",
                    "http://64.225.45.179:3000",
                    "http://127.0.0.1:5000",
                ]
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    )    
    # Session / Security
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = Redis.from_url(Config.redis_connection)
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # seconds
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY
    # DB (switch)
    #for production
    '''app.config['SQLALCHEMY_DATABASE_URI'] = Config.databse_connection_string'''
    #for dev
    app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///' + os.path.join(basedir, 'database.db')
    # AWS S3
    s3_client = boto3.client('s3', region_name=Config.bucket_region, aws_access_key_id=Config.bucket_access_key, aws_secret_access_key=Config.bucket_secret_key)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    session_ext.init_app(app)
    babel.init_app(app)
    celery_ext.init_app(app)
    jwt.init_app(app)
    init_mail(app)
    init_sentry()
    init_email_fallback(app)


    # Security
    authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Add 'Bearer <your_token>'"
        }
    }
    # Swagger API
    api = Api(
        app,
        version="1.0",
        title="Talius API",
        description="Auto-documented API",
        authorizations=authorizations,
        security="Bearer Auth",
        doc="/"
    )

    # Register Blueprints (one for each _api folder)
    from core.routes.endpoints import api_ns
    api.add_namespace(api_ns, path="/api/talius")

    # Register error handlers globally
    register_error_handlers(app)
    
    return app
