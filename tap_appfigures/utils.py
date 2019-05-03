"""
Misc. utilities
"""

import copy

from dateutil.parser import parse


def date_to_str(value):
    """
    Convert data to standard string format
    """
    return value.strftime("%Y-%m-%d %H:%M:%S")


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
            except ValueError:
                pass

    return result


class RequestError(Exception):
    """
    Error class for raising an error when a
    request to the AppFigures API fails
    """
