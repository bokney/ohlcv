
import pandas
from datetime import datetime

from .manager import OHLCVManager
from .timeframe import Timeframe

__all__ = ["get_ohlcv_data", "OHLCVManager"]

def get_ohlcv_data(
    pair: str,
    timeframe: Timeframe,
    start: datetime,
    end: datetime
) -> pandas.DataFrame:
    manager = OHLCVManager()
    return manager.get_ohlcv_data(pair, timeframe, start, end)
