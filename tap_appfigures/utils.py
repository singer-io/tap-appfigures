"""
Misc. utilities
"""

import copy
import math

from dateutil.parser import parse


def str_to_date(value):
    """
    Convert string to date
    """
    return parse(value)


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


def tidy_dates(row_dict):
    """
    Product rows contain dates in  2018-12-18T17:14:07 format
    The Stitch target needs a Z at the end of the dates
    i.e. 2018-12-18T17:14:07Z
    """
    result = copy.deepcopy(row_dict)
    for key, value in result.items():
        if isinstance(value, dict):
            result[key] = tidy_dates(value)
        elif (key.endswith('_date') or key.endswith('_timestamp')) and value:
            result[key] = value + 'Z'
    return result
