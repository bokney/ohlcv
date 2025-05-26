
import logging
import pandas as pd
from typing import List
from pathlib import Path
from datetime import datetime

from .timeframe import Timeframe
from .model import OHLCVData

logger = logging.getLogger(__name__)


class OHLCVWarehouse:
    def __init__(self, db_path: Path = Path("data/ohlcv_data.db")):
        pass

    def _ensure_db_directory(self) -> None:
        pass

    def _ensure_table_exists(self) -> None:
        pass

    def close(self) -> None:
        pass

    def store_ohlcv_data(
        self, pair: str, timeframe: Timeframe, data: List[OHLCVData]
    ) -> None:
        pass

    def load_ohlcv_data(
        self, pair: str, timeframe: Timeframe, start: datetime, end: datetime
    ) -> pd.DataFrame:
        return pd.DataFrame()
