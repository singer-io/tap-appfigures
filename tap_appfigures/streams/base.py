"""
Stream base class
"""
import inspect
import os
from copy import deepcopy

import singer

from tap_appfigures.utils import str_to_date, strings_to_floats, RequestError, dates_to_str, date_to_str


def stream_details_from_catalog(catalog, stream_name):
    """
    Extract details for a single stream from the catalog
    """
    for stream_details in catalog.streams:
        if stream_details.tap_stream_id == stream_name:
            return stream_details
    return None


class Record:
    """
    Stores one input-record, and returns in a few different formats
    """
    DATE_FIELDS = ['date']

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.clean_data = self.create_clean_data(raw_data)
        self.for_export = dates_to_str(self.clean_data)

    def create_clean_data(self, raw_data):
        clean_data = deepcopy(raw_data)
        clean_data = strings_to_floats(clean_data)
        for date_field in self.DATE_FIELDS:
            clean_data[date_field] = str_to_date(clean_data[date_field])
        return clean_data

    @property
    def bookmark(self):
        return self.clean_data['date']


class AppFiguresBase:
    """
    Stream base class
    """
    BASE_URL = "https://api.appfigures.com/v2/"
    STREAM_NAME = ''
    URI = ''
    KEY_PROPERTIES = []
    RESPONSE_LEVELS = 2
    RECORD_CLASS = Record

    def __init__(self, client, state, catalog):
        self.schema = None

        if catalog:
            stream_details = stream_details_from_catalog(catalog, self.STREAM_NAME)
            if stream_details:
                self.schema = stream_details.schema.to_dict()
                self.key_properties = stream_details.key_properties

        if not self.schema:
            self.schema = singer.utils.load_json(
                os.path.normpath(
                    os.path.join(
                        self.get_class_path(),
                        '../schemas/{}.json'.format(self.STREAM_NAME))))
            self.key_properties = self.KEY_PROPERTIES

        self.client = client
        self.state = state
        bookmark_date = singer.bookmarks.get_bookmark(
            state=state,
            tap_stream_id=self.STREAM_NAME,
            key='last_record'
        )
        if not bookmark_date:
            bookmark_date = client.start_date

        self.bookmark_date = str_to_date(bookmark_date)

        self.product_ids = []

    def sync(self):
        """
        Perform sync action
        These steps are the same for all streams
        Differences between streams are implemented by overriding .do_sync() method
        """
        singer.write_schema(self.STREAM_NAME, self.schema, self.key_properties)
        self.do_sync()
        singer.write_state(self.state)

    @staticmethod
    def traverse_nested_dicts(dict_, levels):
        """
        The typical response from API requests is a series of nested dictionaries
        Flatten this and return as an iterator
        """
        for x in dict_.values():
            for y in x.values():

                # The dict_ is nested two or three levels deep
                if levels == 3:
                    for z in y.values():
                        yield z
                else:
                    yield y

    def do_sync(self):
        """
        Main sync functionality
        Most of the streams use this
        A few of the streams work differently and override this method
        """
        try:
            response = self.client.make_request(self.URI.format(self.bookmark_date.strftime('%Y-%m-%d')))
        except RequestError:
            return

        new_bookmark_date = self.bookmark_date

        with singer.metrics.Counter('record_count', {'endpoint': self.STREAM_NAME}) as counter:
            for entry in self.traverse_nested_dicts(response.json(), self.RESPONSE_LEVELS):
                record = self.RECORD_CLASS(entry)
                new_bookmark_date = max(new_bookmark_date, record.bookmark)
                singer.write_record(self.STREAM_NAME, record.for_export)
            counter.increment()

        self.state = singer.write_bookmark(self.state, self.STREAM_NAME, 'last_record', date_to_str(new_bookmark_date))

    def get_class_path(self):
        """
        The absolute path of the source file for this class
        """
        return os.path.dirname(inspect.getfile(self.__class__))

    def generate_catalog(self):
        """
        Builds the catalog entry for this stream
        """
        return dict(
            tap_stream_id=self.STREAM_NAME,
            stream=self.STREAM_NAME,
            key_properties=self.key_properties,
            schema=self.schema,
            # metadata={
            #     'selected': True,
            #     'schema-name': self.STREAM_NAME,
            #     'is_view': False,
            # }
        )
