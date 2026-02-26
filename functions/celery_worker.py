from celery import Celery
from config import Config
import ssl

class CeleryExt:
    def __init__(self, app=None):
        self.celery = Celery(__name__)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        broker_url = Config.redis_connection
        result_backend = Config.redis_connection

        ssl_options = None
        if broker_url.startswith("rediss://"):
            ssl_options = {"ssl_cert_reqs": ssl.CERT_NONE}  # 👈 accept Valkey SSL

        self.celery.conf.update(
            broker_url=broker_url,
            result_backend=result_backend,
            broker_use_ssl=ssl_options,
            redis_backend_use_ssl=ssl_options,
        )

        class ContextTask(self.celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        self.celery.Task = ContextTask

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['celery'] = self.celery

celery_ext = CeleryExt()