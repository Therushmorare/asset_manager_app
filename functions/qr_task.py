from functions.celery_worker import celery_ext
from core.api.asset_code_gen import generate_qr_per_asset
from flask import current_app

@celery_ext.celery.task
def generate_qr_per_asset_task(asset_id):
    try:
        generate_qr_per_asset(asset_id)
    except Exception as e:
        current_app.logger.error(f"QR Generation Failed: {e}")