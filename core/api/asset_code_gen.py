"""
Generate QR Code (Batch Safe Version)
"""

from model.asset import Asset
from functions.qr_gen import qr_code
from functions.file_uploder import file_upload
from database import db
from model.qr_codes import AssetQRCodes
from functions.celery_worker import celery_ext
from flask import current_app

#generate for bulk import
@celery_ext.celery.task(bind=True)
def generate_qr_code(self, batch_size=500):
    try:
        with current_app.app_context():

            assets = (
                Asset.query
                .filter(Asset.qr_code.is_(None))
                .limit(batch_size)
                .all()
            )

            if not assets:
                return "No assets require QR generation"

            for asset in assets:
                try:
                    image = qr_code(asset.asset_id)

                    if not image:
                        continue

                    qr_url = file_upload(image, asset.asset_id)

                    qr_data = AssetQRCodes(
                        asset_id=asset.asset_id,
                        url=qr_url,
                        status='ACTIVE'
                    )

                    db.session.add(qr_data)
                    asset.qr_code = qr_url

                except Exception as inner_error:
                    print(f"QR generation failed for {asset.asset_id}: {inner_error}")
                    continue

            db.session.commit()

            return f"Generated QR for {len(assets)} assets"

    except Exception as e:
        db.session.rollback()
        print(f"Asset QR Assign Error: {e}")
        raise

#generate for individual asset
def generate_qr_per_asset(asset_id):
    try:
        asset = Asset.query.filter_by(asset_id=asset_id).first()
        if not asset:
            return {'message': 'Asset does not exist'}, 404
        
        image = qr_code(asset.asset_id)

        if not image:
            return {'message': 'Could not generate qr code for asset'}, 400
        
        qr_url = file_upload(image, asset.asset_id)

        qr_data = AssetQRCodes(
            asset_id=asset.asset_id,
            url=qr_url,
            status='ACTIVE'
        )

        db.session.add(qr_data)
        asset.qr_code = qr_url

        db.session.commit()

        return {'message': 'Asset QR Code Generated Successfully'}, 200
    
    except Exception as e:
        db.session.rollback()
        print(f"QR Code Per Asset Error:{e}")
        return {'message': 'Somthing went wrong'}
