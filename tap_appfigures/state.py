"""
Maintain the state - mostly the bookmarks

Code copied from tap-framework, version 0.1.0 - then adapted
"""
import datetime
import json
import os

import singer

from dateutil.parser import parse

LOGGER = singer.get_logger()


class State:
    """
    Holds the state data
    """
    def __init__(self, state_file=None):
        self.state = {}

        # Remember the state file, so we can refresh the state on completion
        self.state_file = state_file

        # We're using a (singleton) instance of State() as a handy way to
        # retain the list of product_ids. There is probably a tidier
        # way to do this
        self.product_ids = []

        self.load()

    def load(self):
        """
        Load the state from the state_file
        """

        # This should never happen - state is a required argument
        if self.state_file is None:
            return

        if not os.path.isfile(self.state_file):
            LOGGER.warning(
                'State file [{}] does not exist. '
                'A new state file will be created'.format(self.state_file)
            )
            return

        try:
            with open(self.state_file) as handle:
                try:
                    self.state = json.load(handle)
                except Exception as e:
                    LOGGER.warning(
                        'Could not decode state file [{}]. '
                        'Is it valid JSON? Error {}'.format(self.state_file, e)
                    )
        except Exception as e:
            LOGGER.fatal('Could not open state file [{}], error {}'.format(self.state_file, e))
            raise RuntimeError

    def save(self):
        """
        Save the state to the state file
        """

        # This should never happen - state is a required argument
        if not self.state_file:
            return

        LOGGER.info('Updating state to {}.'.format(self.state_file))

        singer.write_state(self.state_file)
        try:
            with open(self.state_file, 'w') as output_file:
                try:
                    json.dump(self.state, output_file)
                except Exception as e:
                    LOGGER.fatal('Failed to write state to file, error {}'.format(e))
        except Exception as e:
            LOGGER.fatal('Failed to write state file [{}], error {}'.format(self.state_file, e))
            raise RuntimeError

    def bookmark_for_stream(self, stream_name):
        """
        Return the bookmark for the given stream
        If not available, return None
        """
        bookmark = self.state.get('bookmarks', {}) \
            .get(stream_name, {}) \
            .get('last_record')

        if bookmark is None:
            return None

        return parse(bookmark)

    def set_bookmark_for_stream(self, stream_name, field, value):
        """
        Set or update the bookmark for the given stream
        """
        if value is None:
            return

        if isinstance(value, datetime.datetime):
            parsed = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            parsed = parse(value).strftime("%Y-%m-%d %H:%M:%S")

        if 'bookmarks' not in self.state:
            self.state['bookmarks'] = {}

        if (self.state['bookmarks'].get(stream_name, {}).get('last_record') is None or
                self.state['bookmarks'].get(stream_name, {}).get('last_record') < parsed):
            self.state['bookmarks'][stream_name] = {
                'field': field,
                'last_record': parsed,
            }
