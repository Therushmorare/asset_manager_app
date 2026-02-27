"""
Add platform users
"""
from api.account_checker import check_user

def add_admin(admin_id, email, first_name, last_name, employee_number, department, role, phone_number):
    try:
        