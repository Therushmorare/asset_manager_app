# validators.py
from datetime import datetime
from asset_template import TEMPLATE_FIELDS

def validate_row(row: dict):
    errors = []
    validated_data = {}
    
    for field, rules in TEMPLATE_FIELDS.items():
        value = row.get(field)
        
        # Check required
        if rules.get("required") and (value is None or str(value).strip() == ""):
            errors.append(f"{field} is required")
            continue
        
        # Skip if value is empty and not required
        if value is None or str(value).strip() == "":
            validated_data[field] = None
            continue
        
        # Type validation
        field_type = rules.get("type")
        try:
            if field_type == int:
                validated_data[field] = int(value)
            elif field_type == float:
                validated_data[field] = float(value)
            elif field_type == "date":
                validated_data[field] = datetime.strptime(value, "%Y-%m-%d").date()
            else:
                validated_data[field] = str(value).strip()
        except Exception:
            errors.append(f"{field} has invalid type or format")
            continue
        
        # Choice validation
        choices = rules.get("choices")
        if choices and validated_data[field] not in choices:
            errors.append(f"{field} must be one of {choices}")
    
    # Logical checks
    if validated_data.get("residual_value") is not None and validated_data.get("cost") is not None:
        if validated_data["residual_value"] > validated_data["cost"]:
            errors.append("residual_value cannot exceed cost")
    
    return validated_data, errors