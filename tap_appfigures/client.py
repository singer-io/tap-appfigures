"""
The AppFigures API client
"""

import sys

import requests

import singer

from tap_appfigures.utils import RequestError

LOGGER = singer.get_logger()


class AppFiguresClient:
    """
    The client
    """
    BASE_URI = "https://api.appfigures.com/v2/"

    def __init__(self, config):
        self.api_key = config.get('api_key')
        self.password = config.get('password')
        self.username = config.get('username')
        self.start_date = config.get('start_date')

    def make_request(self, uri):
        """
        Make a request to BASE_URI/uri
        and handle any errors
        """
        LOGGER.info("Making get request to {}".format(uri))
        headers = {"X-Client-Key": self.api_key}
        auth = (self.username, self.password)
        try:
            print(self.BASE_URI + uri.lstrip("/"))
            """
            response = requests.get(
                self.BASE_URI + uri.lstrip("/"),
                auth=auth,
                headers=headers
            )
            """
        except Exception as e:
            LOGGER.error('Error [{}], request {} failed'.format(e, uri))
            raise RequestError
        """
        if response.status_code == 420:
            LOGGER.critical('Daily rate limit reached, after request for {}'.format(uri))
            sys.exit(1)
        
        
        response.raise_for_status()
        return response
        """
        return None
