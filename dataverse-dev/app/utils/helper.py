import datetime
from re import sub


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()


# string format to date-time object.
def str_to_datetime(date: str):
    return datetime.datetime.strptime(date, '%d-%m-%Y').date()
