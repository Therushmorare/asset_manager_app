from functions.celery_worker import celery_ext
from database import db
from models.asset import Asset, DepreciationEntry
from datetime import datetime
from core.api.depreciation_engine import *

@celery_ext.celery.task(bind=True)
def run_depreciation(self, period=None):
    """
    Calculate depreciation for eligible assets and store entries.
    period: string like '2026-02'; defaults to current month.
    """

    if period is None:
        period = datetime.utcnow().strftime("%Y-%m")

    try:
        # Only ACTIVE depreciable assets
        assets = Asset.query.filter(
            Asset.status == "ACTIVE"
        ).yield_per(50)  # batching

        for asset in assets:

            # ---- Prevent duplicate depreciation for same period ----
            existing_entry = DepreciationEntry.query.filter_by(
                asset_id=asset.asset_id,
                period=period
            ).first()

            if existing_entry:
                continue  # Skip already processed asset

            # ---- Prevent depreciating below residual ----
            book_value = asset.current_book_value or asset.cost

            if book_value <= asset.residual_value:
                continue  # Fully depreciated

            dep_amount = 0

            # ---- Calculate based on method ----
            if asset.depreciation_method == "STRAIGHT_LINE":
                dep_amount = straight_line_method(
                    asset.cost,
                    asset.residual_value,
                    asset.useful_life_years
                )
                book_value -= dep_amount

            elif asset.depreciation_method == "REDUCING_BALANCE":
                dep_amount, book_value = reducing_balance(
                    book_value,
                    rate=asset.depreciation_rate or 20
                )

            elif asset.depreciation_method == "UNITS_OF_PRODUCTION":
                dep_amount, book_value = units_of_production(
                    asset.cost,
                    asset.useful_life_years,
                    asset.total_units,
                    asset.units_used
                )

            # ---- Final Safety Clamp ----
            if book_value < asset.residual_value:
                dep_amount -= (asset.residual_value - book_value)
                book_value = asset.residual_value

            # ---- Save depreciation entry ----
            entry = DepreciationEntry(
                asset_id=asset.asset_id,
                period=period,
                depreciation_amount=round(dep_amount, 2),
                book_value=round(book_value, 2)
            )

            db.session.add(entry)

            # ---- Update asset ----
            asset.current_book_value = round(book_value, 2)

        db.session.commit()

        return f"Depreciation completed for period {period}"

    except Exception as e:
        db.session.rollback()
        self.retry(exc=e, countdown=60, max_retries=3)