from datetime import datetime

def is_valid_date_format(date, format):
    try:
        datetime.strptime(date, format)
        return True
    except ValueError:
        return False