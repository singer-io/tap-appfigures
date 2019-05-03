"""
The task runner
Implements the do_sync() and do_discover() actions
"""

import json
import sys

import singer

from tap_appfigures.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()


class AppFiguresRunner:
    """
    The task runner
    """
    def __init__(self, client, state, catalog):
        self.client = client
        self.state = state
        self.streams = [Stream(client, state, catalog) for Stream in AVAILABLE_STREAMS]

    def do_discover(self):
        """
        Creates and outputs the catalog
        """
        LOGGER.info("Starting discovery.")

        catalog = [
            stream.generate_catalog()
            for stream in self.streams
        ]

        json.dump({'streams': catalog}, sys.stdout, indent=4)

    @staticmethod
    def sync_stream(stream):
        """
        Sync a single stream
        """
        try:
            stream.sync()
        except OSError as e:
            LOGGER.error(str(e))
            exit(e.errno)

        except Exception as e:
            LOGGER.error(str(e))
            LOGGER.error('Failed to sync endpoint {}, moving on!'
                         .format(stream.STREAM_NAME))
            raise e

    def do_sync(self):
        """
        Sync all streams
        :return:
        """
        LOGGER.info("Starting sync.")

        # We need the list of product ids for the rankings report
        # so sync the products first
        for stream in self.streams:
            if stream.STREAM_NAME == 'products':
                self.sync_stream(stream)

        # Sync all but the products
        for stream in self.streams:
            if stream.STREAM_NAME != 'products':
                self.sync_stream(stream)
