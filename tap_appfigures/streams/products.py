import singer

from tap_appfigures.streams.base import AppFiguresBase
from tap_appfigures.utils import str_to_date, date_to_str, tidy_dates


class ProductsStream(AppFiguresBase):
    STREAM_NAME = 'products'
    KEY_PROPERTIES = ['id']

    def do_sync(self):
        bookmark_date_as_date = str_to_date(self.bookmark_date)
        max_product_date = bookmark_date_as_date

        product_response = self.client.make_request("/products/mine")
        product_ids = []
        with singer.metrics.Counter('record_count', {'endpoint': 'products'}) as counter:

            for product in product_response.json().values():
                product_ids.append(product['id'])

                # Only upsert messages which have changed
                product_date = product['updated_date'] if product['updated_date']\
                    else product['added_date']
                product_date = str_to_date(product_date)

                product = tidy_dates(product)

                if product_date > bookmark_date_as_date:
                    singer.write_message(singer.RecordMessage(
                        stream='products',
                        record=product,
                    ))
                max_product_date = max(max_product_date, product_date)

                counter.increment()

        self.state = singer.write_bookmark(self.state, self.STREAM_NAME, 'last_record', date_to_str(max_product_date))

        self.product_ids = product_ids
