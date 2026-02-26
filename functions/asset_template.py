#Template for assets

TEMPLATE_FIELDS = {
    "asset_id": {"required": False, "type": str},
    "description": {"required": True, "type": str},
    "category": {"required": True, "type": str},
    "sub_category": {"required": False, "type": str},
    "department": {"required": True, "type": str},
    "custodian": {"required": True, "type": str},
    "location": {"required": True, "type": str},
    "acquisition_date": {"required": True, "type": "date"},  # YYYY-MM-DD
    "cost": {"required": True, "type": float},
    "residual_value": {"required": True, "type": float},
    "useful_life_years": {"required": True, "type": int},
    "depreciation_method": {"required": True, "type": str, "choices": ["STRAIGHT_LINE", "REDUCING_BALANCE", "UNITS_PRODUCTION"]}
}