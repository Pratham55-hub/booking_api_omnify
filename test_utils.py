# ==============================================================================
#  FILE: test_utils.py
#  DESCRIPTION: Unit tests for utility functions.
# ==============================================================================
import pytest
import datetime
import pytz
from app.utils import to_utc, from_utc, DEFAULT_TZ

def test_to_utc_conversion():
    """
    Tests if a naive local datetime object is correctly converted to a UTC string.
    """
    local_dt = datetime.datetime(2025, 10, 26, 10, 0, 0) # 10:00 AM IST
    expected_utc_str = "2025-10-26 04:30:00"
    converted_utc_str = to_utc(local_dt, DEFAULT_TZ)
    assert converted_utc_str == expected_utc_str

def test_from_utc_conversion():
    """
    Tests if a UTC datetime string is correctly converted to a localized string.
    """
    utc_str = "2025-11-03 20:00:00" # 8:00 PM UTC
    target_tz = pytz.timezone("America/New_York")
    expected_local_str = "2025-11-03 15:00:00 EST-0500"
    converted_local_str = from_utc(utc_str, target_tz)
    assert converted_local_str == expected_local_str

def test_from_utc_with_daylight_saving():
    """
    Tests if the from_utc conversion correctly handles Daylight Saving Time.
    """
    # A UTC time that falls within Daylight Saving Time for New York (EDT, UTC-4)
    utc_str_dst = "2025-07-08 14:00:00" # 2:00 PM UTC
    
    target_tz = pytz.timezone("America/New_York")
    
    # Expected local time is 10:00 AM EDT
    expected_local_str_dst = "2025-07-08 10:00:00 EDT-0400"
    
    converted_local_str = from_utc(utc_str_dst, target_tz)
    
    # FIX: The variable name in the assertion is now correct.
    assert converted_local_str == expected_local_str_dst

def test_from_utc_handles_none():
    """
    Tests that from_utc returns None if given None.
    """
    assert from_utc(None, DEFAULT_TZ) is None
