from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage
from core.api.asset_importer import import_assets
from core.api.add_asset import add_asset
from core.api.add_users import add_user
from core.api.asset_disposal import *
from core.api.asset_scanner import scan_asset
from core.api.asset_verification import verify_asset
from core.api.delete_users import delete_user
from core.api.depreciation_schedular import run_depreciation
from core.api.edit_asset import edit_asset
from core.api.edit_users import edit_user
from core.auth.auth import signin_applicants
from core.mfa.verify_mfa_code import verify_mfa_code
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from functions.form_sanitizer import sanitize_input
from core.auth.resend_mfa import resend_mfa
from core.auth.forgot_password import *
from core.queries.general_queries import *

limiter = Limiter(get_remote_address, default_limits=["100 per hour"], storage_uri= Config.redis_connection)
"""
------------------------------------------------------------------------------------------
MAIN ROUTES FOR App
------------------------------------------------------------------------------------------
"""

api_ns = Namespace("App", description="App API endpoints")

# ------------------------------
# Models
# -------------------------------
asset_model = api_ns.model('Asset', {
    'added_by': fields.String,
    'asset_id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'category': fields.String,
    'sub_category': fields.String,
    'department': fields.String,
    'custodian': fields.String,
    'location': fields.String,
    'acquisition_date': fields.String,
    'cost': fields.Float,
    'residual_value': fields.Float,
    'useful_life_years': fields.Integer,
    'depreciation_method': fields.String,
    'qr_code': fields.String,
    'status': fields.String,
    'disposal_date': fields.String,
    'disposal_value': fields.Float,
    'gain_loss': fields.Float,
    'created_at': fields.String,
    'updated_at': fields.String
})

login_model = api_ns.model("LoginRequest", {
    "email": fields.String(required=True, example="admin@example.com"),
    "password": fields.String(required=True, example="StrongPassword123"),
    "user_type": fields.String(
        required=True,
        enum=["admin", "asset_manager", "asset_controller", "custodian"]
    )
})

login_response = api_ns.model("LoginResponse", {
    "message": fields.String,
    "email": fields.String,
    "user_type": fields.String,
    "user_id": fields.String,
    "access_token": fields.String
})

upload_parser = api_ns.parser()
upload_parser.add_argument(
    "file",
    location="files",
    type=FileStorage,
    required=True,
    help="CSV file containing assets"
)

asset_create_model = api_ns.model("CreateAsset", {
    "user_id": fields.String(required=True, description="User performing the action"),
    "name": fields.String(required=True),
    "description": fields.String(required=True),
    "category": fields.String(required=True),
    "sub_category": fields.String(required=True),
    "department": fields.String(required=True),
    "custodian": fields.String(required=True),
    "location": fields.String(required=True),
    "acquisition_date": fields.String(required=True, description="YYYY-MM-DD"),
    "cost": fields.Float(required=True),
    "residual_value": fields.Float(required=True),
    "useful_life_years": fields.Integer(required=True),
    "depreciation_method": fields.String(
        required=True,
        enum=["STRAIGHT_LINE", "REDUCING_BALANCE", "UNITS_OF_PRODUCTION"]
    )
})

user_create_model = api_ns.model("CreateUser", {
    "email": fields.String(required=True),
    "first_name": fields.String(required=True),
    "last_name": fields.String(required=True),
    "department": fields.String(required=True),
    "role": fields.String(required=True, description="Role depends on user_type"),
    "phone_number": fields.String(required=True),
    "user_type": fields.String(
        required=True,
        enum=["ADMIN", "ASSET_CONTROLLER", "ASSET_MANAGER", "CUSTODIAN"]
    ),
    "adder_id": fields.String(
        required=False,
        description="Admin ID performing this action"
    )
})

disposal_request_model = api_ns.model("DisposalRequest", {
    "manager_id": fields.String(required=True, description="ID of the asset manager"),
    "asset_id": fields.String(required=True, description="ID of the asset to dispose"),
    "reason_for_disposal": fields.String(required=True),
    "proposed_disposal_method": fields.String(
        required=True,
        description="Proposed method of disposal"
    ),
    "date": fields.String(required=True, description="Date of disposal request, YYYY-MM-DD"),
    "proceeds": fields.Float(required=False, default=0),
    "supporting_docs": fields.String(required=False, description="Optional document URLs or base64")
})

admin_disposal_model = api_ns.model("AdminDisposalApproval", {
    "admin_id": fields.String(required=True, description="Admin performing approval"),
    "disposal_id": fields.String(required=True, description="Disposal request ID"),
    "status": fields.String(
        required=True,
        enum=["APPROVED", "REJECTED"],
        description="Approval status"
    )
})

scan_asset_response_model = api_ns.model("ScanAssetResponse", {
    "asset_id": fields.String,
    "name": fields.String,
    "description": fields.String,
    "category": fields.String,
    "asset_department": fields.String,
    "location": fields.String,
    "status": fields.String
})

verify_asset_model = api_ns.model("VerifyAssetRequest", {
    "custodian_id": fields.String(required=True, description="Custodian user ID"),
    "asset_id": fields.String(required=True, description="Asset unique ID"),
    "status": fields.String(
        required=True,
        enum=["ACTIVE", "DAMAGED", "MISSING", "DESTROYED", "DISPOSED"],
        description="Updated asset status"
    ),
    "description": fields.String(required=True, description="Verification notes or comments")
})

verify_asset_response = api_ns.model("VerifyAssetResponse", {
    "message": fields.String(description="Response message")
})

delete_user_model = api_ns.model("DeleteUserRequest", {
    "requester_id": fields.String(
        required=True,
        description="Admin performing the deletion"
    ),
    "user_id": fields.String(
        required=True,
        description="Target user ID to delete"
    ),
    "user_type": fields.String(
        required=True,
        enum=["ADMIN", "ASSET_MANAGER", "ASSET_CONTROLLER", "CUSTODIAN"],
        description="Type of user being deleted"
    )
})

delete_user_response = api_ns.model("DeleteUserResponse", {
    "message": fields.String(description="Response message")
})

run_depreciation_model = api_ns.model("RunDepreciationRequest", {
    "period": fields.String(
        required=False,
        description="Depreciation period in format YYYY-MM (defaults to current month)",
        example="2026-02"
    )
})

run_depreciation_response = api_ns.model("RunDepreciationResponse", {
    "message": fields.String,
    "task_id": fields.String
})

edit_asset_model = api_ns.model("EditAssetRequest", {
    "name": fields.String(required=False),
    "description": fields.String(required=False),
    "category": fields.String(required=False),
    "sub_category": fields.String(required=False),
    "department": fields.String(required=False),
    "custodian": fields.String(required=False),
    "location": fields.String(required=False),
    "acquisition_date": fields.String(required=False, description="YYYY-MM-DD"),
    "cost": fields.Float(required=False),
    "residual_value": fields.Float(required=False),
    "useful_life_years": fields.Integer(required=False),
    "depreciation_method": fields.String(
        required=False,
        enum=["STRAIGHT_LINE", "REDUCING_BALANCE", "UNITS_OF_PRODUCTION"]
    ),
    "status": fields.String(required=False)
})

edit_asset_response = api_ns.model("EditAssetResponse", {
    "message": fields.String
})

edit_user_model = api_ns.model("EditUserRequest", {
    "email": fields.String(required=False),
    "first_name": fields.String(required=False),
    "last_name": fields.String(required=False),
    "department": fields.String(required=False),
    "phone_number": fields.String(required=False),
    "role": fields.String(required=False),
    "is_active": fields.Boolean(required=False),
    "mfa_required": fields.Boolean(required=False)
})

edit_user_response = api_ns.model("EditUserResponse", {
    "message": fields.String
})

mfa_verify_model = api_ns.model("MfaVerifyRequest", {
    "user_id": fields.String(
        required=True,
        description="Unique ID of the user to verify the MFA code for",
        example="123e4567-e89b-12d3-a456-426614174000"
    ),
    "code": fields.String(
        required=True,
        description="MFA code sent to the user via email or SMS",
        example="482913"
    )
})

mfa_verify_success_model = api_ns.model("MfaVerifySuccess", {
    "message": fields.String(
        description="Status message for MFA verification",
        example="MFA code verified successfully"
    ),
    "verified": fields.Boolean(
        description="Whether the MFA code is valid",
        example=True
    ),
    "token": fields.String(
        description="JWT token returned after successful MFA verification",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
})

error_model = api_ns.model('ErrorResponse', {
    'message': fields.String(example='Something went wrong')
})

resend_mfa_model = api_ns.model('ResendMFA', {
    'email': fields.String(required=True, description='User email address'),
    'user_type': fields.String(
        required=True,
        description='Type of user',
        enum=['ADMIN', 'ASSET_MANAGER', 'ASSET_CONTROLLER', 'CUSTODIAN']
    )
})

forgot_password_model = api_ns.model('ForgotPassword', {
    'email': fields.String(required=True, description='User email for password reset')
})

verify_password_model = api_ns.model('VerifyPassword', {
    'email': fields.String(required=True, description='User email'),
    'token': fields.String(required=True, description='Token sent via email')
})
# -----------------------------
# Endpoints
# -----------------------------
@api_ns.route("/importAssets/<string:uid>")
class AssetImport(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(upload_parser)
    @api_ns.response(202, "Import started")
    @api_ns.response(400, "Validation Error")
    @api_ns.doc(description="Bulk import assets via CSV file")
    def post(self, uid):

        user_id = uid
        if not user_id:
            return {"message": "Authentication required"}, 401

        args = upload_parser.parse_args()
        file = args.get("file")

        if not file:
            return {"message": "Please provide asset csv file"}, 400

        if not file.filename.endswith(".csv"):
            return {"message": "Only CSV files allowed"}, 400

        csv_content = file.read()

        # Trigger Celery async task
        task = import_assets.delay(user_id=user_id, csv_content=csv_content)

        return {
            "message": "Asset import started",
            "task_id": task.id
        }, 202

@api_ns.route("/addAsset")
class AssetCreate(Resource):

    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(asset_create_model)
    @api_ns.response(201, "Asset created successfully")
    @api_ns.response(400, "Validation Error")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(500, "Server error")
    def post(self):

        data = request.json

        response, status_code = add_asset(
            user_id=data.get("user_id"),
            name=sanitize_input(data.get("name")),
            description=sanitize_input(data.get("description")),
            category=sanitize_input(data.get("category")),
            sub_category=sanitize_input(data.get("sub_category")),
            department=sanitize_input(data.get("department")),
            custodian=sanitize_input(data.get("custodian")),
            location=sanitize_input(data.get("location")),
            acquisition_date=sanitize_input(data.get("acquisition_date")),
            cost=sanitize_input(data.get("cost")),
            residual_value=sanitize_input(data.get("residual_value")),
            useful_life_years=sanitize_input(data.get("useful_life_years")),
            depreciation_method=sanitize_input(data.get("depreciation_method")),
        )

        return response, status_code
    
@api_ns.route("/addUser")
class UserCreate(Resource):

    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(user_create_model)
    @api_ns.response(201, "User created successfully")
    @api_ns.response(400, "Validation Error")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(500, "Server error")
    def post(self):

        data = request.json

        response, status_code = add_user(
            email=sanitize_input(data.get("email")),
            first_name=sanitize_input(data.get("first_name")),
            last_name=sanitize_input(data.get("last_name")),
            department=sanitize_input(data.get("department")),
            role=sanitize_input(data.get("role")),
            phone_number=sanitize_input(data.get("phone_number")),
            user_type=sanitize_input(data.get("user_type")),
            adder_id=data.get("adder_id")
        )

        return response, status_code
    
@api_ns.route("/backDoor")
class UserCreate(Resource):

    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(user_create_model)
    @api_ns.response(201, "User created successfully")
    @api_ns.response(400, "Validation Error")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(500, "Server error")
    def post(self):

        data = request.json

        response, status_code = add_user(
            email=sanitize_input(data.get("email")),
            first_name=sanitize_input(data.get("first_name")),
            last_name=sanitize_input(data.get("last_name")),
            department=sanitize_input(data.get("department")),
            role=sanitize_input(data.get("role")),
            phone_number=sanitize_input(data.get("phone_number")),
            user_type=sanitize_input(data.get("user_type"))
        )

        return response, status_code
    

@api_ns.route("/disposalRequest")
class AssetDisposal(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(disposal_request_model)
    @api_ns.response(201, "Disposal request lodged successfully")
    @api_ns.response(400, "Validation error or duplicate request")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "Asset not found")
    @api_ns.response(500, "Server error")
    def post(self):
        """
        Asset manager files a disposal request for an asset.
        """
        data = request.json

        response, status_code = asset_disposal_request(
            manager_id=data.get("manager_id"),
            asset_id=data.get("asset_id"),
            reason_for_disposal=sanitize_input(data.get("reason_for_disposal")),
            proposed_disposal_method=sanitize_input(data.get("proposed_disposal_method")),
            date=sanitize_input(data.get("date")),
            proceeds=sanitize_input(data.get("proceeds")),
            supporting_docs=data.get("supporting_docs")
        )

        return response, status_code
    
@api_ns.route("/approveDisposal")
class AdminDisposalApproval(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(admin_disposal_model)
    @api_ns.response(200, "Disposal request processed successfully")
    @api_ns.response(400, "Validation error / Already processed")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "Disposal request or asset not found")
    @api_ns.response(500, "Server error")
    def post(self):
        """
        Admin approves or rejects a pending asset disposal request.
        """
        data = request.json

        response, status_code = admin_disposal_approve(
            admin_id=data.get("admin_id"),
            disposal_id=data.get("disposal_id"),
            status=data.get("status")
        )

        return response, status_code
    
@api_ns.route("/scan/<string:asset_id>")
class ScanAsset(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.response(200, "Asset scanned successfully", scan_asset_response_model)
    @api_ns.response(404, "Asset not found or offline")
    @api_ns.response(500, "Server error")
    def get(self, asset_id):
        """
        Scan an asset by its ID. Only active assets are returned.
        """
        response, status_code = scan_asset(asset_id)
        return response, status_code
    
@api_ns.route("/verifyAsset")
class VerifyAsset(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(verify_asset_model)
    @api_ns.response(200, "Asset verified successfully", verify_asset_response)
    @api_ns.response(400, "Validation error / Invalid asset state")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "Asset not found")
    @api_ns.response(500, "Server error")
    @api_ns.doc(description="Custodian verifies an asset and updates its status")
    def post(self):
        """
        Verify an asset and update its operational status.
        """
        data = request.json

        response, status_code = verify_asset(
            custodian_id=data.get("custodian_id"),
            asset_id=data.get("asset_id"),
            status=data.get("status"),
            description=sanitize_input(data.get("description"))
        )

        return response, status_code
    
@api_ns.route("/deleteUser")
class DeleteUser(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(delete_user_model)
    @api_ns.response(200, "User deleted successfully", delete_user_response)
    @api_ns.response(400, "Validation error")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "User not found")
    @api_ns.response(500, "Server error")
    @api_ns.doc(description="Admin deletes (soft deletes) a system user")
    def post(self):
        """
        Soft delete a user account. Only admins can perform this action.
        """
        data = request.json

        response, status_code = delete_user(
            requester_id=data.get("requester_id"),
            user_id=data.get("user_id"),
            user_type=data.get("user_type")
        )

        return response, status_code

@api_ns.route("/depreciationSchedular/<string:aid>")
class RunDepreciation(Resource):
    @limiter.limit("10 per minute")
    #@jwt_required()
    @api_ns.expect(run_depreciation_model)
    @api_ns.response(202, "Depreciation job started", run_depreciation_response)
    @api_ns.response(403, "Unauthorized")
    @api_ns.response(500, "Server error")
    @api_ns.doc(description="Trigger monthly depreciation run (Admin only)")
    def post(self, aid):
        """
        Trigger depreciation calculation for a given period.
        Runs asynchronously via Celery.
        """

        current_user_id = aid

        # ---- Permission Check ----
        admin = AdminUser.query.filter_by(admin_id=current_user_id).first()
        if not admin:
            return {"message": "Only admins can run depreciation"}, 403

        data = request.json or {}
        period = data.get("period")

        # ---- Trigger Async Task ----
        task = run_depreciation.delay(period=period)

        return {
            "message": "Depreciation job started",
            "task_id": task.id
        }, 202

@api_ns.route("/<string:asset_id>")
class EditAsset(Resource):
    @limiter.limit("10 per minute")
    @jwt_required()
    @api_ns.expect(edit_asset_model)
    @api_ns.response(200, "Asset updated successfully", edit_asset_response)
    @api_ns.response(400, "Validation error")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "Asset not found")
    @api_ns.response(500, "Server error")
    @api_ns.doc(description="Edit asset details (Manager, Controller, or Admin only)")
    def patch(self, asset_id):
        """
        Update asset details. Only editable fields will be updated.
        """

        user_id = get_jwt_identity()
        updates = request.json or {}

        response, status_code = edit_asset(
            user_id=user_id,
            asset_id=asset_id,
            **updates
        )

        return response, status_code
    

@api_ns.route("/<string:user_type>/<string:user_id>")
class EditUser(Resource):
    @limiter.limit("10 per minute")
    @jwt_required()
    @api_ns.expect(edit_user_model)
    @api_ns.response(200, "User updated successfully", edit_user_response)
    @api_ns.response(400, "Invalid user type")
    @api_ns.response(403, "Permission denied")
    @api_ns.response(404, "User not found")
    @api_ns.response(500, "Server error")
    @api_ns.doc(params={
        "user_type": "ADMIN | ASSET_MANAGER | ASSET_CONTROLLER | CUSTODIAN",
        "user_id": "ID of the user to edit"
    })
    @api_ns.doc(description="Admin edits user account details")
    def patch(self, user_type, user_id):
        """
        Update user account information.
        Only ADMIN users can perform this action.
        """

        editor_id = get_jwt_identity()
        updates = request.json or {}

        response, status_code = edit_user(
            editor_id=editor_id,
            user_id=user_id,
            user_type=user_type,
            **updates
        )

        return response, status_code
    
@api_ns.route("/login")
class Login(Resource):
    @limiter.limit("10 per minute")
    @api_ns.expect(login_model)
    @api_ns.response(200, "Login successful", login_response)
    @api_ns.response(401, "Invalid credentials")
    @api_ns.response(404, "User not found")
    @api_ns.response(500, "Server error")
    @api_ns.doc(description="Authenticate user and receive JWT token")
    def post(self):
        """
        Login user and return JWT access token.
        """

        data = request.json

        email = sanitize_input(data.get("email"))
        password = sanitize_input(data.get("password"))
        user_type = sanitize_input(data.get("user_type"))

        if user_type not in ["admin", "asset_manager", "asset_controller", "custodian"]:
            return {"message": "Invalid user type"}, 400

        response, status_code = signin_applicants(
            email=email,
            password=password,
            user_type=user_type
        )

        return response, status_code
    
@api_ns.route('/resend-mfa')
class ResendMFAResource(Resource):

    @api_ns.expect(resend_mfa_model)
    @api_ns.doc(
        description="Resend MFA code to user's email",
        responses={
            200: 'Success',
            400: 'Bad request',
            404: 'User not found',
            500: 'Internal server error'
        }
    )
    def post(self):
        data = api_ns.payload

        email = data.get('email')
        user_type = data.get('user_type')

        response, status_code = resend_mfa(email, user_type)

        return response, status_code

@api_ns.route('/verify-mfa')
class VerifyMfaResource(Resource):

    @api_ns.doc(
        description="Verify the MFA code for a user after login. Returns JWT token if successful.",
        responses={
            200: ("MFA verified", mfa_verify_success_model),
            400: ("Validation error", error_model),
            401: ("Invalid or expired MFA code", error_model)
        }
    )
    @api_ns.expect(mfa_verify_model, validate=True)
    def post(self):
        """
        MFA Verification Endpoint
        --------------------------
        Validates a Multi-Factor Authentication (MFA) code sent to the user.

        **Flow:**
        1. Validate incoming request body.
        2. Call `verify_mfa_code(user_id, code)` service.
        3. Return success response with JWT token if verification passes.
        """
        data = request.json

        result, status = verify_mfa_code(
            user_id=data.get("user_id"),
            code=data.get("code")
        )

        return result, status
    
@api_ns.route('/forgot-password')
class ForgotPasswordResource(Resource):
    @api_ns.expect(forgot_password_model)
    @api_ns.doc(
        description="Send MFA code to user email to reset password",
        responses={
            200: "Success",
            400: "Missing email",
            404: "User not found",
            500: "Internal server error"
        }
    )
    def post(self):
        data = api_ns.payload
        email = data.get('email')
        
        response, status_code = forgot_password(email)
        return response, status_code


@api_ns.route('/verify-password')
class VerifyPasswordResource(Resource):
    @api_ns.expect(verify_password_model)
    @api_ns.doc(
        description="Verify token and reset password automatically",
        responses={
            200: "Password reset successful",
            400: "Missing token",
            404: "User not found",
            500: "Verification failed"
        }
    )
    def post(self):
        data = api_ns.payload
        email = data.get('email')
        token = data.get('token')

        response, status_code = verify_to_password(email, token)
        return response, status_code

@api_ns.route('/getAssets')
class GetAssets(Resource):

    @api_ns.doc(
        description="Retrieve all assets in the system",
        responses={
            200: "Assets retrieved successfully",
            404: "No assets found",
            500: "Internal server error"
        }
    )
    def get(self):
        response, status_code = get_assets()
        return response, status_code