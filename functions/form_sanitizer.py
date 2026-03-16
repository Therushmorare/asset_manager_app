import bleach

"""
Function to mask form data
"""

def sanitize_input(user_input):
    return bleach.clean(user_input, tags=[], attributes={}, strip=True)