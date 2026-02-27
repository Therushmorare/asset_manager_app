from functions.celery_worker import celery_ext
from database import db
from model.asset import Asset, DepreciationEntry
from datetime import datetime
from api.depreciation_engine import *

@celery_ext.celery.task
def run_depreciation(period=None):
    """
    Calculate depreciation for all assets and store entries.
    period: string like '2026-02'; defaults to current month
    """
    if period is None:
        period = datetime.now().strftime("%Y-%m")

    try:
        assets = Asset.query.all()
        for asset in assets:
            dep_amount = 0
            book_value = asset.current_book_value or asset.cost

            if asset.depreciation_method == 'STRAIGHT_LINE':
                dep_amount = straight_line_method(asset.cost, asset.residual_value, asset.useful_life_years)
                book_value -= dep_amount

            elif asset.depreciation_method == 'REDUCING_BALANCE':
                dep_amount, book_value = reducing_balance(book_value, rate=20)  # Example: 20% rate

            elif asset.depreciation_method == 'UNITS_OF_PRODUCTION':
                dep_amount, book_value = units_of_production(
                    asset.cost,
                    asset.useful_life_years,
                    asset.total_units,
                    asset.units_used
                )

            # Avoid negative book value
            book_value = max(book_value, asset.residual_value)

            # Save entry
            entry = DepreciationEntry(
                asset_id=asset.asset_id,
                period=period,
                depreciation_amount=dep_amount,
                book_value=book_value
            )
            db.session.add(entry)

            # Update asset's current book value
            asset.current_book_value = book_value

        db.session.commit()
        print(f"Depreciation run completed for period {period}")

    except Exception as e:
        db.session.rollback()
        print(f"Depreciation run failed: {e}")