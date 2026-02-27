import uuid
from database import db
from model.asset import Asset
from model.verification import AssetVerification
from model.custodian import Custodian

def verify_asset(custodian_id, asset_id, status, description):
    try:
        # Check for missing fields
        if any(x is None for x in [custodian_id, asset_id, status, description]):
            return {'message': 'Please check for missing fields'}, 400

        # Check custodian exists
        custodian = Custodian.query.filter_by(user_id=custodian_id).first()
        if not custodian:
            return {'message': 'You don’t have permission to perform this action'}, 403

        # Check asset exists
        asset = Asset.query.filter_by(asset_id=asset_id).first()
        if not asset:
            return {'message': 'Asset does not exist'}, 404

        # Check if asset is not already disposed/destroyed/missing
        last_verification = AssetVerification.query.filter_by(asset_id=asset_id).order_by(AssetVerification.created_at.desc()).first()
        if last_verification and last_verification.status in ['DISPOSED', 'DESTROYED', 'MISSING']:
            return {'message': f"Cannot verify asset; current status is {last_verification.status}"}, 400

        # Insert new verification
        verification_id = str(uuid.uuid4())
        save_data = AssetVerification(
            asset_id=asset_id,
            custodian_id=custodian_id,
            verification_id=verification_id,
            status=status,
            description=description
        )

        db.session.add(save_data)
        db.session.commit()

        return {'message': 'Asset verified successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Asset verification error: {e}")
        return {'message': 'Something went wrong'}, 500