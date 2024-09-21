from datetime import datetime


def calculate_vehicle_age(invoice_date: str):
    days_in_year = 365.2425  # To incorporate leap year no. of days in year are 365.2425
    invoice_date = datetime.strptime(invoice_date, '%d-%m-%Y')
    age_in_years = int((datetime.now() - invoice_date).days / days_in_year)
    return age_in_years
