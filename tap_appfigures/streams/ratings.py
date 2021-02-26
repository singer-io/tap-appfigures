from tap_appfigures.streams.base import AppFiguresBase


class RatingsStream(AppFiguresBase):
    STREAM_NAME = 'ratings'
    URI = '/reports/ratings?group_by=product,country,date&start_date={}&granularity=daily'
    KEY_PROPERTIES = ['product_id', 'country', 'date']
