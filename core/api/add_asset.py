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

def add_asset(user_id, name, description, category, sub_category,
              department, custodian, location, acquisition_date,
              cost, residual_value, useful_life_years, depreciation_method):

    try:
        # ---- Required field check ----
        required_fields = [
            name, description, category, sub_category,
            department, custodian, location,
            acquisition_date, cost,
            residual_value, useful_life_years,
            depreciation_method
        ]

        if any(x is None for x in required_fields):
            return {'message': 'Please fill out all inputs'}, 400

        # ---- Permission check ----
        user = (
            AssetManager.query.filter_by(manager_id=user_id).first()
            or AssetController.query.filter_by(controller_id=user_id).first()
            or AdminUser.query.filter_by(admin_id=user_id).first()
        )

        if not user:
            return {'message': 'You do not have permission to perform this action!'}, 403

        # ---- Business Validation ----
        cost = float(cost)
        residual_value = float(residual_value)
        useful_life_years = int(useful_life_years)

        if cost <= 0:
            return {'message': 'Cost must be greater than 0'}, 400

        if residual_value < 0 or residual_value > cost:
            return {'message': 'Residual value must be between 0 and cost'}, 400

        if useful_life_years <= 0:
            return {'message': 'Useful life must be greater than 0'}, 400

        if depreciation_method not in VALID_METHODS:
            return {'message': 'Invalid depreciation method'}, 400

        # ---- Generate Asset ID ----
        asset_id = str(uuid.uuid4())

        # ---- Create Asset ----
        new_asset = Asset(
            added_by=user_id,
            asset_id=asset_id,
            name=name,
            description=description,
            category=category,
            sub_category=sub_category,
            department=department,
            custodian=custodian,
            location=location,
            acquisition_date=acquisition_date,
            cost=cost,
            residual_value=residual_value,
            useful_life_years=useful_life_years,
            depreciation_method=depreciation_method,
            status='ACTIVE'
        )

        db.session.add(new_asset)
        db.session.commit()

        # ---- Trigger QR Generation (Background Task) ----
        generate_qr_per_asset_task.delay(asset_id)

        log_applicant_track(user_id, 'ASSET MANAGER/ ASSET CONTROLLER/ ADMIN with this ID:{user_id}, added a new asset with the following asset ID:{asset_id}')

        return {
            'message': 'Added asset successfully',
            'asset_id': asset_id
        }, 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Asset Add Error: {e}")
        return {'message': 'Something went wrong'}, 500