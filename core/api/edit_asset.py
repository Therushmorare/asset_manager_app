import uuid
from flask import current_app
from database import db
from models.asset import Asset
from models.admin import AdminUser
from models.asset_manager import AssetManager
from models.asset_controller import AssetController
from functions.qr_task import generate_qr_per_asset_task
from functions.user_logs import log_applicant_track

VALID_METHODS = ["STRAIGHT_LINE", "REDUCING_BALANCE", "UNITS_OF_PRODUCTION"]

def edit_asset(user_id, asset_id, **updates):
    """
    user_id: person editing the asset
    asset_id: asset being edited
    updates: fields to update
    """

    try:
        # ---- Permission Check ----
        user = (
            AssetManager.query.filter_by(manager_id=user_id).first()
            or AssetController.query.filter_by(controller_id=user_id).first()
            or AdminUser.query.filter_by(admin_id=user_id).first()
        )

        if not user:
            return {'message': 'You do not have permission to perform this action!'}, 403

        # ---- Fetch Asset ----
        asset = Asset.query.filter_by(asset_id=asset_id).first()

        if not asset:
            return {'message': 'Asset not found'}, 404

        # ---- Prevent Editing Disposed Assets ----
        if asset.status in ['DISPOSED', 'DESTROYED']:
            return {'message': 'Cannot edit disposed or destroyed asset'}, 400

        # ---- Allowed Editable Fields ----
        allowed_fields = [
            "name", "description", "category", "sub_category",
            "department", "custodian", "location",
            "acquisition_date", "cost",
            "residual_value", "useful_life_years",
            "depreciation_method", "status"
        ]

        # ---- Track if financial fields changed ----
        financial_change = False

        for field, value in updates.items():
            if field in allowed_fields and value is not None:

                # Business Validation for financial fields
                if field == "cost":
                    value = float(value)
                    if value <= 0:
                        return {'message': 'Cost must be greater than 0'}, 400
                    financial_change = True

                if field == "residual_value":
                    value = float(value)
                    if value < 0:
                        return {'message': 'Residual value cannot be negative'}, 400
                    financial_change = True

                if field == "useful_life_years":
                    value = int(value)
                    if value <= 0:
                        return {'message': 'Useful life must be greater than 0'}, 400
                    financial_change = True

                if field == "depreciation_method":
                    if value not in VALID_METHODS:
                        return {'message': 'Invalid depreciation method'}, 400
                    financial_change = True

                setattr(asset, field, value)

        # ---- If cost/residual changed, validate relationship ----
        if asset.residual_value > asset.cost:
            return {'message': 'Residual value cannot exceed cost'}, 400

        # ---- Reset depreciation book value if financial data changed ----
        if financial_change:
            asset.current_book_value = asset.cost

        db.session.commit()

        # ---- Optional: regenerate QR if location or department changed ----
        if any(k in updates for k in ["location", "department"]):
            generate_qr_per_asset_task.delay(asset_id)

        # ---- Log Activity ----
        log_applicant_track(
            user_id,
            "ASSET MANAGER/ ASSET CONTROLER/ ADMIN",
            f"User {user_id} edited asset {asset_id}"
        )

        return {'message': 'Asset updated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Asset Edit Error: {e}")
        return {'message': 'Something went wrong'}, 500