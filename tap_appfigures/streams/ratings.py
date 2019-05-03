from tap_appfigures.streams.base import AppFiguresBase


class RatingsStream(AppFiguresBase):
    STREAM_NAME = 'ratings'
    URI = '/reports/ratings?group_by=products,dates&start_date={}&granularity=daily'
    KEY_PROPERTIES = ['product_id', 'date']
