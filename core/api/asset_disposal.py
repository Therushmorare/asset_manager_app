"""
Asset Disposal
"""
from model.asset_manager import AssetManager
from model.asset import Asset
from functions.file_uploder import file_upload
from model.disposal_ledger import DisposalLedger
from model.admin import AdminUser
from database import db
import uuid
from datetime import datetime, timezone

#asset manager files the request
def asset_disposal_request(manager_id, asset_id, reason_for_disposal, proposed_disposal_method, date, proceeds, supporting_docs):

    try:
        # Validate required fields
        if not all([reason_for_disposal, proposed_disposal_method, date]):
            return {'message': 'Please fill out all required inputs'}, 400

        manager = AssetManager.query.filter_by(manager_id=manager_id).first()
        if not manager:
            return {'message': 'User does not have privileges to perform action'}, 403

        asset = Asset.query.filter_by(asset_id=asset_id).first()
        if not asset:
            return {'message': 'Asset does not exist'}, 404

        # Prevent disposal of already disposed asset
        if asset.status == "DISPOSED":
            return {'message': 'Asset is already disposed'}, 400

        # Department validation
        if manager.department != asset.department:
            return {'message': 'Only asset manager belonging to asset department can file a disposal request'}, 403

        # Prevent duplicate pending request
        existing_request = DisposalLedger.query.filter_by(
            asset_id=asset_id,
            status="REQUEST"
        ).first()

        if existing_request:
            return {'message': 'There is already a pending disposal request for this asset'}, 400

        disposal_id = str(uuid.uuid4())

        url = file_upload(supporting_docs) if supporting_docs else None

        save_data = DisposalLedger(
            asset_id=asset_id,
            disposal_id=disposal_id,
            manager_id=manager_id,
            reason=reason_for_disposal,
            method=proposed_disposal_method,
            date=date,
            proceeds=proceeds or 0,
            url=url,
            status='REQUEST',
        )

        db.session.add(save_data)
        db.session.commit()

        return {'message': 'Disposal request lodged successfully'}, 201

    except Exception as e:
        db.session.rollback()
        print(f"Disposal request error: {e}")
        return {'message': 'Something went wrong'}, 500
    
# admin approval
def admin_disposal_approve(admin_id, disposal_id, status):
    try:
        if status not in ['APPROVED', 'REJECTED']:
            return {'message': 'Select proper status'}, 400

        admin = AdminUser.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return {'message': 'You do not have permission to perform action!'}, 403

        disposal = DisposalLedger.query.filter_by(disposal_id=disposal_id).first()
        if not disposal:
            return {'message': 'Disposal request does not exist'}, 404

        # Only allow action if still pending
        if disposal.status != "REQUEST":
            return {'message': 'This disposal request has already been processed'}, 400

        asset = Asset.query.filter_by(asset_id=disposal.asset_id).first()
        if not asset:
            return {'message': 'Linked asset not found'}, 404

        if status == "APPROVED":

            # Calculate Net Book Value
            net_book_value = asset.cost - asset.accumulated_depreciation

            gain_loss = disposal.proceeds - net_book_value

            # Update asset
            asset.status = "DISPOSED"
            asset.disposal_date = disposal.date
            asset.disposal_value = disposal.proceeds
            asset.gain_loss = gain_loss

            # Freeze depreciation
            asset.is_depreciating = False

            # Store accounting values in ledger
            disposal.net_book_value = net_book_value
            disposal.gain_loss = gain_loss

        disposal.status = status
        disposal.approved_by = admin_id
        disposal.approved_at = datetime.now(timezone.utc)
        db.session.commit()

        return {'message': f'Asset disposal request {status} successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Asset approval error: {e}')
        return {'message': 'Something went wrong'}, 500