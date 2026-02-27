"""
Depreciation Engine
"""

def straight_line_method(cost, residual_value, useful_life):
    cost = float(cost)
    residual_value = float(residual_value)
    useful_life = float(useful_life)
    
    if useful_life <= 0:
        raise ValueError("Useful life must be greater than 0")
    return (cost - residual_value) / useful_life


def reducing_balance(start_period_value, rate):
    start_period_value = float(start_period_value)
    rate = float(rate)
    
    depreciation = start_period_value * (rate / 100)
    book_value = start_period_value - depreciation
    return depreciation, book_value


def units_of_production(cost, residual_value, total_expense_units, units):
    cost = float(cost)
    residual_value = float(residual_value)
    total_expense_units = float(total_expense_units)
    units = float(units)
    
    if total_expense_units <= 0:
        raise ValueError("Total expense units must be greater than 0")
    
    depreciation = ((cost - residual_value) / total_expense_units) * units
    book_value = cost - depreciation
    return depreciation, book_value