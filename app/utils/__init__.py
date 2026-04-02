import random
import string
from datetime import datetime

def generate_ticket_id():
    year = datetime.utcnow().year
    number = ''.join(random.choices(string.digits, k=4))
    return f'JAN-{year}-{number}'