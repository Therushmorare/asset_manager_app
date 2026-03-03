from flask import current_app
import csv
from io import StringIO
from functions.validations import validate_row
from model.asset import Asset
from database import db
from functions.celery_worker import celery_ext
from core.api.asset_code_gen import generate_qr_code
from functions.user_logs import log_applicant_track

MAX_ROWS = 1000

# Transactional inserter
def insert_assets_to_db(all_valid):
    asset_ids = []
    try:
        with db.session.begin():
            for row in all_valid:
                asset = Asset(**row)
                db.session.add(asset)
                db.session.flush()  # ensures asset.id is available
                asset_ids.append(asset.id)
        return True, asset_ids, None
    except Exception as e:
        db.session.rollback()
        return False, [], str(e)


# Celery task
@celery_ext.celery.task(bind=True)
def import_assets(self, user_id, csv_content):
    """
    csv_content: bytes or string of the uploaded CSV
    """
    try:
        if not user_id:
            return {'message': 'Please login to import assets'}, 400

        if not csv_content:
            return {'message': 'Please provide asset csv file'}, 400

        # Decode content if bytes
        if isinstance(csv_content, bytes):
            csv_content = csv_content.decode('utf-8')

        reader = csv.DictReader(StringIO(csv_content))

        all_valid = []
        all_errors = []

        for idx, row in enumerate(reader, start=1):
            if idx > MAX_ROWS:
                all_errors.append({
                    "row": idx,
                    "errors": [f"Exceeded maximum allowed rows per upload ({MAX_ROWS})"]
                })
                break

            validated_row, errors = validate_row(row)
            if errors:
                all_errors.append({"row": idx, "errors": errors})
            else:
                all_valid.append(validated_row)

        # Insert transactionally
        asset_ids = []
        if all_valid:
            success, asset_ids, db_error = insert_assets_to_db(all_valid)
            if not success:
                return {"message": f"Could not upload assets: {db_error}"}, 500

        # Trigger QR generation only for inserted assets
        if asset_ids:
            generate_qr_code.delay(asset_ids=asset_ids)

        log_applicant_track(user_id, 'ASSET MANAGER/ ASSET CONTROLLER/ ADMIN', f'Added bulk asset with the following asset IDs:{asset_ids}')

        return {
            "imported_rows": len(all_valid),
            "failed_rows": len(all_errors),
            "errors": all_errors
        }, 200

    except Exception as e:
        # Ensure rollback if something fails
        db.session.rollback()
        current_app.logger.error(f"Error while importing assets: {e}")
        return {'message': 'Something went wrong'}, 500