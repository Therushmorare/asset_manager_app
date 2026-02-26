import random
import string

def generate_random_string(length):
    # Define the pool of characters to choose from
    # Example: lowercase letters, uppercase letters, and digits
    characters = string.ascii_letters + string.digits 
    
    # Use random.choices to pick 'length' number of characters
    # and then join them to form a string
    random_string = ''.join(random.choices(characters, k=length))
    return random_string