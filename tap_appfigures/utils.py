"""
Misc. utilities
"""

import copy
import math
from datetime import datetime

from dateutil.parser import parse
from pytz import timezone


def str_to_date(value):
    """
    Convert (json) string to date
    """

    # This might be upsetting because there is no T ie: '2019-03-31' -> '2019-03-31 00:00:00-0500'
    result = parse(value)
    if result.tzinfo is None:
        # All dates (so far) are EST, but this is not part of the data returned by the API
        result = timezone('EST').localize(result)
    return result


def date_to_str(value):
    """
    Convert date to (json) string
    """
    return value.strftime("%Y-%m-%d %H:%M:%S%z")


def strings_to_floats(row_dict):
    """
    Some imported rows contain floats represented as strings
    e.g. "0.00"
    Convert all of these to actual floats
    """
    result = copy.copy(row_dict)
    for key, value in result.items():
        if isinstance(value, str):
            try:
                result[key] = float(value)

                # The Stitch target can't handle NaN, and needs a None (null) instead
                if math.isnan(result[key]):
                    result[key] = None

            # Not all fields are numeric fields. Just ignore those
            except ValueError:
                pass

    return result


class RequestError(Exception):
    """
    Error class for raising an error when a
    request to the AppFigures API fails
    """


def dates_to_str(row_dict):
    """
    Convert all dates to strings - recursively
    """
    result = copy.deepcopy(row_dict)
    for key, value in result.items():
        if isinstance(value, dict):
            result[key] = dates_to_str(value)
        elif isinstance(value, datetime):
            result[key] = date_to_str(value)
    return result
