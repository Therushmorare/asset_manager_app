from flask import jsonify, render_template, request
from database import db

def wants_json_response():
    """Check if request is hitting the API namespace."""
    return request.path.startswith("/api")


def register_error_handlers(app):

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error("❌ Unhandled Exception", exc_info=error)

        if wants_json_response():
            return {
                "error": "Internal Server Error",
                "message": "There was an error, admin has been notified",
                "status": 500
            }, 500

    @app.errorhandler(503)
    def service_unavailable(error):
        app.logger.error("❌ Service Went Down", exc_info=error)

        if wants_json_response():
            return {
                "error": "Service Unavailable",
                "message": "Service is currently unavailable.",
                "status": 503
            }, 503

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error("❌ Broken Page", exc_info=error)

        if wants_json_response():
            return {
                "error": "Not Found",
                "message": "The requested resource was not found.",
                "status": 404
            }, 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        app.logger.error("❌ Rate Limite Exceeded", exc_info=error)
        if wants_json_response():
            return {
                "error": "Rate Limit",
                "message": "Rate limit exceeded",
                "status": 429
            }, 429