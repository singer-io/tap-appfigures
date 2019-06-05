from datetime import date, timedelta

import singer

from tap_appfigures.streams.base import AppFiguresBase, Record
from tap_appfigures.utils import date_to_str


class RanksStream(AppFiguresBase):
    STREAM_NAME = 'ranks'
    KEY_PROPERTIES = ['product_id', 'country', 'category', 'date']

    def do_sync(self):
        start_date = self.bookmark_date
        new_bookmark_date = self.bookmark_date
        product_ids = ';'.join(str(id) for id in self.product_ids)

        while start_date.date() <= date.today():
            end_date = start_date + timedelta(days=28)
            uri = '/ranks/{}/daily/{}/{}'.format(
                product_ids,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            data = self.client.make_request(uri).json()

            rank_dates = data['dates']
            rank_data = data['data']

            with singer.metrics.Counter('record_count', {'endpoint': 'ranks'}) as counter:
                for rank_entry in rank_data:
                    for i, rank_date in enumerate(rank_dates):
                        record = Record(dict(
                            country=rank_entry['country'],
                            category=rank_entry['category'],
                            product_id=rank_entry['product_id'],
                            position=rank_entry['positions'][i],
                            delta=rank_entry['deltas'][i],
                            date=rank_date,
                        ))

                        new_bookmark_date = max(new_bookmark_date, record.bookmark)
                        singer.write_message(singer.RecordMessage(
                            stream=self.STREAM_NAME,
                            record=record.for_export,
                        ))
                        counter.increment()

            self.state = singer.write_bookmark(
                self.state, self.STREAM_NAME, 'last_record', date_to_str(new_bookmark_date)
            )

            start_date = end_date
