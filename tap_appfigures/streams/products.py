import singer

from tap_appfigures.streams.base import AppFiguresBase, Record
from tap_appfigures.utils import date_to_str


class ProductRecord(Record):
    DATE_FIELDS = ['release_date', 'added_date', 'updated_date']
    @property
    def product_date(self):
        if self.clean_data['updated_date']:
            return self.clean_data['updated_date']
        return self.clean_data['added_date']


class ProductsStream(AppFiguresBase):
    STREAM_NAME = 'products'
    KEY_PROPERTIES = ['id']

    def do_sync(self):
        max_product_date = self.bookmark_date

        product_response = self.client.make_request("/products/mine")
        product_ids = []
        with singer.metrics.Counter('record_count', {'endpoint': 'products'}) as counter:

            for product in product_response.json().values():
                record = ProductRecord(product)
                product_ids.append(record.clean_data['id'])

                # Only upsert messages which have changed
                if record.product_date > self.bookmark_date:
                    singer.write_message(singer.RecordMessage(
                        stream='products',
                        record=record.for_export,
                    ))
                    max_product_date = max(max_product_date, record.product_date)

                    counter.increment()

        self.state = singer.write_bookmark(self.state, self.STREAM_NAME, 'last_record', date_to_str(max_product_date))

        self.product_ids = product_ids
