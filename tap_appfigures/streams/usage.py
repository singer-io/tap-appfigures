from tap_appfigures.streams.base import AppFiguresBase


class UsageStream(AppFiguresBase):
    STREAM_NAME = 'usage'
    URI = '/reports/usage/?group_by=network,product,date&start_date={}'
    RESPONSE_LEVELS = 3
    KEY_PROPERTIES = ['product_id', 'date', 'store']
