import random
import string

def generate_license():
    license_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return license_code