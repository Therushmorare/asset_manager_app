# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_login import LoginManager
from flask_session import Session
from flask_babel import Babel
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
cache = Cache()
limiter = Limiter(key_func=lambda: "global")  # override in app
session_ext = Session()
babel = Babel()
jwt = JWTManager()