# error_handlers.py
import logging
from logging.handlers import SMTPHandler
from flask import Flask
from config import Config

def init_sentry():
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        if Config.SENTRY_DSN:
            sentry_sdk.init(
                dsn=Config.SENTRY_DSN,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
                environment="production"
            )
            print("✅ Sentry initialized.")
        else:
            print("⚠️  Sentry DSN not set. Skipping.")
    except ImportError:
        print("❌ Sentry SDK not installed. Run `pip install sentry-sdk`.")

def init_email_fallback(app: Flask):
    if not app.debug and not Config.SENTRY_DSN:
        mail_handler = SMTPHandler(
            mailhost=(Config.MAIL_SERVER, Config.MAIL_PORT),
            fromaddr="noreply@propsho.co.za",
            toaddrs="tshego.tt.morare@gmail.com",
            subject="🔥 Production Error Alert (No Sentry)",
            credentials=(Config.MAIL_USERNAME, Config.MAIL_PASSWORD),
            secure=()
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        print("📧 Email fallback logger initialized.")