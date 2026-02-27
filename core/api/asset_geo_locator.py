"""
Asset locator
"""
from model.asset import Asset
from geopy.geocoders import Nominatim

"""
Asset locator
"""
from model.asset import Asset
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def asset_locator(asset_id):
    try:
        asset = Asset.query.filter_by(asset_id=asset_id).first()

        if not asset:
            return {'message': 'Asset does not exist'}, 404
        
        if not asset.location:
            return {'message': 'Asset location not set'}, 400

        geo = Nominatim(user_agent="talius_asset_manager")
        location = geo.geocode(asset.location)

        if location is None:
            return {
                'message': 'Could not find accurate asset location, please update asset register'
            }, 404

        return {
            'asset_id': asset.asset_id,
            'address': location.address,
            'latitude': location.latitude,
            'longitude': location.longitude
        }, 200

    except (GeocoderTimedOut, GeocoderServiceError):
        return {
            'message': 'Geocoding service temporarily unavailable'
        }, 503

    except Exception as e:
        print(f"Geolocation error: {e}")
        return {
            'message': 'Internal server error'
        }, 500