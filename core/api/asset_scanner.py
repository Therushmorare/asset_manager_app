"""
Scan Asset
"""

from model.asset import Asset

def scan_asset(asset_id):
    try:
        asset = Asset.query.get(asset_id)
        if not asset:
            return {"error": "Asset not found"}, 404
        
        if asset.status != 'ACTIVE':
            return {'message': 'Asset data is offline'}, 404
        
        # Optionally include audit logging here
        # log_scan(asset_id, current_user.id)
        
        return {
            "asset_id": asset.asset_id,
            "name": asset.name,
            "description": asset.description,
            "category": asset.category,
            "asset_department": asset.department,
            "location": asset.location,
            "status": asset.status
        }, 200
    except Exception as e:
        print(f"Asset Scan Error:{e}")
        return {'message': 'Something went wrong'}