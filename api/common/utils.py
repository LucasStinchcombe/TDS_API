# coding=utf-8
"""
Utilities for TDS API
"""
from datetime import datetime
import re

def toyota_req(res):
    """
    Filters out expired session responses.
    """
    res.encoding = 'shift_jis'

    if re.search('接続を切りました', res.text):
        return None

    return res


def get_datetime(month, day, hour=0, minute=0):
    """
    Get datetime given just month, day, hour.

    Toyota Driving School website does not display year so it is inferred
    from current year and month displayed.
    """

    cur_year = datetime.now().year
    cur_month = datetime.now().month

    year = cur_year
    if cur_month == 12 and month != 12:
        year += 1

    return datetime(year, month, day, hour, minute)
