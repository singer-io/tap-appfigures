from collections import OrderedDict

from tap_appfigures.streams.base import AppFiguresBase
import inspect
import os
import itertools

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
        Allows for differences in schemas between catalog and the actual received data to unravel lists
        This permits the user to get more granular ratings info (e.g. number of reviews for each rating)
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

                    schema_keys = [x for x in self.schema['properties'].keys() if x not in entry.keys()]
                    entry_keys = [x for x in entry.keys() if x not in self.schema['properties'].keys() and not x.endswith('percent')]
                    if schema_keys and entry_keys:
                        entries = list(itertools.chain.from_iterable([entry[entry_item] for entry_item in entry_keys]))
                        for j, schema_item in enumerate(schema_keys):
                            entry[schema_item] = entries[j]
                        for key in entry_keys:
                            del(entry[key])

                    entry = strings_to_floats(entry)

                    singer.write_message(singer.RecordMessage(
                        stream=self.STREAM_NAME,
                        record=entry,
                    ))
                counter.increment()

            self.state = singer.write_bookmark(self.state, self.STREAM_NAME, 'last_record', new_bookmark_date)
            if end_date == datetime.date.today() - datetime.timedelta(days=1):
                break
            start_date = end_date.strftime('%Y-%m-%d')
