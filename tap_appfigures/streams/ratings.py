from collections import OrderedDict

from tap_appfigures.streams.base import AppFiguresBase
import inspect
import os

import singer
import datetime

from tap_appfigures.utils import str_to_date, strings_to_floats, RequestError


class RatingsStream(AppFiguresBase):
    STREAM_NAME = 'ratings'
    URI = '/reports/ratings?group_by=product,country,date&start_date={}&end_date={}&granularity=daily'
    RESPONSE_LEVELS = 3
    KEY_PROPERTIES = ['product_id', 'country', 'date']

    def do_sync(self):
        """
        Main sync functionality
        Most of the streams use this
        A few of the streams work differently and override this method
        """
        start_date = str_to_date(self.bookmark_date).strftime('%Y-%m-%d')

        while str_to_date(start_date).date() < datetime.date.today():
            end_date = min(str_to_date(start_date).date() + datetime.timedelta(days=28),
                           datetime.date.today() - datetime.timedelta(days=1))

            try:
                response = self.client.make_request(self.URI.format(start_date, end_date.strftime('%Y-%m-%d')))
            except RequestError:
                return

            new_bookmark_date = self.bookmark_date
            with singer.metrics.Counter('record_count', {'endpoint': self.STREAM_NAME}) as counter:
                for entry in self.traverse_nested_dicts(response.json(), self.RESPONSE_LEVELS):
                    new_bookmark_date = max(new_bookmark_date, entry['date'])
                    entry = strings_to_floats(entry)
                    schema_keys = [x for x in self.schema['properties'].keys() if x not in entry.keys()]
                    entry_keys = [x for x in entry.keys() if x not in self.schema['properties'].keys()]
                    for i, entry_item in enumerate(entry_keys):
                    #for entry_item in entry[entry_keys]:
                        for j, schema_item in enumerate(schema_keys):
                            print("foo: ", i, entry_item, j, schema_item)

                    # singer.write_message(singer.RecordMessage(
                    #     stream=self.STREAM_NAME,
                    #     record=entry,
                    # ))
                counter.increment()

            self.state = singer.write_bookmark(self.state, self.STREAM_NAME, 'last_record', new_bookmark_date)
            if end_date == datetime.date.today() - datetime.timedelta(days=1):
                break
            start_date = end_date.strftime('%Y-%m-%d')
