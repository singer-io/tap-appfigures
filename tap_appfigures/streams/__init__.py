from .products import ProductsStream
from .sales import SalesStream
from .revenue import RevenueStream
from .ratings import RatingsStream
from .usage import UsageStream
from .ranks import RanksStream

AVAILABLE_STREAMS = [
    ProductsStream,
    SalesStream,
    RevenueStream,
    RatingsStream,
    UsageStream,
    RanksStream,
]
