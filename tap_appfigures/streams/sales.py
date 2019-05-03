from tap_appfigures.streams.base import AppFiguresBase


class SalesStream(AppFiguresBase):
    STREAM_NAME = 'sales'
    URI = '/reports/sales/?group_by=products,dates&start_date={}&granularity=daily'
    KEY_PROPERTIES = ['product_id', 'date']
