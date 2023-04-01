from datetime import datetime

def calculate_age(date_of_birth):
    today = datetime.utcnow()
    age = today.year - date_of_birth.year
    if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
        age -= 1
    return age