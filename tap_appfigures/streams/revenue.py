from tap_appfigures.streams.base import AppFiguresBase


class RevenueStream(AppFiguresBase):
    STREAM_NAME = 'revenue'
    URI = '/reports/revenue?group_by=products,dates&start_date={}&granularity=daily'
    KEY_PROPERTIES = ['product_id', 'date']
