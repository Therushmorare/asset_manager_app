from flask import Flask, request, jsonify
import csv
from io import StringIO
from functions.validations import validate_row
from model.asset import Asset
from database import db
from functions.celery_worker import celery_ext

"""
Asset Importer
"""

#inserter
def insert_assets_to_db(all_valid):
    try:
        with db.session.begin():  # transaction starts here
            for row in all_valid:
                asset = Asset(**row)  # map CSV row to Asset model
                db.session.add(asset)
        # commit happens automatically at the end of 'with' block
        return True, None
    except Exception as e:
        db.session.rollback()  # rollback if anything fails
        return False, str(e)

#importer
@celery_ext.celery.task
def import_assets(user_id, csv_file):
    try:
        if user_id is None:
            return {'message': 'Please login to import assets'}, 400
        
        if not csv_file:
            return {'message': 'Please provide asset csv file'}, 400
        
        content = csv_file.read().decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        
        all_valid = []
        all_errors = []
        MAX_ROWS = 1000
        
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
        if all_valid:
            if all_valid:
                success, db_error = insert_assets_to_db(all_valid)
            if not success:
                return {"message": "Could not upload assets"}, 500
            
        return {
            "imported_rows": len(all_valid),
            "failed_rows": len(all_errors),
            "errors": all_errors
        }, 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while importing assets: {e}")
        return {'message': 'Something went wrong'}, 500