# -*- coding: utf-8 -*-
"""
Tests for helper functions in the cython tslibs.offsets
"""
from datetime import datetime

import pytest

from pandas._libs import tslib
from pandas import Timestamp

import pandas._libs.tslibs.offsets as liboffsets


def test_get_lastbday():
    dt = datetime(2017, 11, 30)
    assert dt.weekday() == 3  # i.e. this is a business day
    wkday, days_in_month = tslib.monthrange(dt.year, dt.month)
    assert liboffsets.get_lastbday(wkday, days_in_month) == 30

    dt = datetime(1993, 10, 31)
    assert dt.weekday() == 6  # i.e. this is not a business day
    wkday, days_in_month = tslib.monthrange(dt.year, dt.month)
    assert liboffsets.get_lastbday(wkday, days_in_month) == 29


def test_get_firstbday():
    dt = datetime(2017, 4, 1)
    assert dt.weekday() == 5  # i.e. not a weekday
    wkday, days_in_month = tslib.monthrange(dt.year, dt.month)
    assert liboffsets.get_firstbday(wkday, days_in_month) == 3

    dt = datetime(1993, 10, 1)
    assert dt.weekday() == 4  # i.e. a business day
    wkday, days_in_month = tslib.monthrange(dt.year, dt.month)
    assert liboffsets.get_firstbday(wkday, days_in_month) == 1


def test_shift_month():
    dt = datetime(2017, 11, 30)
    assert liboffsets.shift_month(dt, 0, 'business_end') == dt
    assert liboffsets.shift_month(dt, 0,
                                  'business_start') == datetime(2017, 11, 1)

    ts = Timestamp('1929-05-05')
    assert liboffsets.shift_month(ts, 1, 'start') == Timestamp('1929-06-01')
    assert liboffsets.shift_month(ts, -3, 'end') == Timestamp('1929-02-28')

    assert liboffsets.shift_month(ts, 25, None) == Timestamp('1931-06-5')

    # Try to shift to April 31, then shift back to Apr 30 to get a real date
    assert liboffsets.shift_month(ts, -1, 31) == Timestamp('1929-04-30')

    dt = datetime(2017, 11, 15)

    assert liboffsets.shift_month(dt, 0, day_opt=None) == dt
    assert liboffsets.shift_month(dt, 0, day_opt=15) == dt

    assert liboffsets.shift_month(dt, 1,
                                  day_opt='start') == datetime(2017, 12, 1)

    assert liboffsets.shift_month(dt, -145,
                                  day_opt='end') == datetime(2005, 10, 31)

    with pytest.raises(ValueError):
        liboffsets.shift_month(dt, 3, day_opt='this should raise')


def test_get_day_of_month():
    # get_day_of_month is not directly exposed; we test it via roll_yearday
    dt = datetime(2017, 11, 15)

    with pytest.raises(ValueError):
        # To hit the raising case we need month == dt.month and n > 0
        liboffsets.roll_yearday(dt, n=3, month=11, day_opt='foo')


def test_roll_yearday():
    # Copied from doctest examples
    month = 3
    day_opt = 'start'              # `other` will be compared to March 1
    other = datetime(2017, 2, 10)  # before March 1
    assert liboffsets.roll_yearday(other, 2, month, day_opt) == 1
    assert liboffsets.roll_yearday(other, -7, month, day_opt) == -7
    assert liboffsets.roll_yearday(other, 0, month, day_opt) == 0

    other = Timestamp('2014-03-15', tz='US/Eastern')  # after March 1
    assert liboffsets.roll_yearday(other, 2, month, day_opt) == 2
    assert liboffsets.roll_yearday(other, -7, month, day_opt) == -6
    assert liboffsets.roll_yearday(other, 0, month, day_opt) == 1

    month = 6
    day_opt = 'end'                # `other` will be compared to June 30
    other = datetime(1999, 6, 29)  # before June 30
    assert liboffsets.roll_yearday(other, 5, month, day_opt) == 4
    assert liboffsets.roll_yearday(other, -7, month, day_opt) == -7
    assert liboffsets.roll_yearday(other, 0, month, day_opt) == 0

    other = Timestamp(2072, 8, 24, 6, 17, 18)  # after June 30
    assert liboffsets.roll_yearday(other, 5, month, day_opt) == 5
    assert liboffsets.roll_yearday(other, -7, month, day_opt) == -6
    assert liboffsets.roll_yearday(other, 0, month, day_opt) == 1
