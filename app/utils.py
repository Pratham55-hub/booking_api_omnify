# ==============================================================================
#  FILE: app/utils.py
#  DESCRIPTION: Utility and helper functions.
# ==============================================================================
import datetime
import pytz

# It's best practice to store all datetime information in UTC in the database.
UTC = pytz.utc
# Set a default timezone for creating classes if not specified.
DEFAULT_TZ = pytz.timezone('Asia/Kolkata') # IST

def to_utc(dt, tz):
    """Converts a naive datetime object to a UTC string for DB storage."""
    return tz.localize(dt).astimezone(UTC).strftime('%Y-%m-%d %H:%M:%S')

def from_utc(utc_str, tz):
    """Converts a UTC string from the DB to a localized datetime string."""
    if not utc_str:
        return None
    # Assuming the string from DB is naive UTC, make it aware.
    dt_utc = UTC.localize(datetime.datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S'))
    return dt_utc.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
