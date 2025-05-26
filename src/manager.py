
import logging
import pandas as pd
from typing import Optional, List, Tuple
from datetime import datetime, timedelta, timezone

from .warehouse import OHLCVWarehouse
from .moralis_api import MoralisAPI
from .timeframe import Timeframe
from .model import OHLCVData

logger = logging.getLogger(__name__)


class OHLCVManager:
    def __init__(
        self,
        moralis_api: Optional[MoralisAPI] = None,
        ohlcv_warehouse: Optional[OHLCVWarehouse] = None
    ):
        self._moralis_api = moralis_api or MoralisAPI()
        self._ohlcv_warehouse = ohlcv_warehouse or OHLCVWarehouse()

    def _timestamps_to_spans(
        self, missing: pd.DatetimeIndex, delta: timedelta
    ) -> List[Tuple[datetime, datetime]]:
        spans: List[Tuple[datetime, datetime]] = []
        if missing.empty:
            return spans

        span_start = prev = missing[0]

        for ts in missing[1:]:
            if ts - prev == delta:
                prev = ts
                continue

            spans.append(
                (span_start.to_pydatetime(), (prev + delta).to_pydatetime())
            )
            span_start = prev = ts

        spans.append(
            (span_start.to_pydatetime(), (prev + delta).to_pydatetime())
        )
        return spans

    def _to_utc(self, dt: datetime) -> datetime:
        return (
            dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None
            else dt.astimezone(timezone.utc)
        )

    def _fetch_ohlcv_data(
        self, pair: str, timeframe: Timeframe, start: datetime, end: datetime
    ) -> List[OHLCVData]:
        from_date = self._to_utc(start)
        to_date = self._to_utc(end)

        all_data = []
        count = 0

        while True:
            if to_date < from_date:
                logger.info("Reached the lower date limit; exiting loop.")
                break

            count += 1

            logger.debug(
                f"Fetching OHLCV data from {from_date.isoformat()} "
                f"to {to_date.isoformat()} (iteration {count})"
            )

            data = self._moralis_api.get_ohlcv_data(
                pair_address=pair,
                timeframe=timeframe.value,
                currency="usd",
                from_date=from_date,
                to_date=to_date
            )

            if not data:
                logger.info("No data received; exiting loop.")
                break

            all_data.extend(data)

            oldest_timestamp = min(item.timestamp for item in data)
            if oldest_timestamp >= to_date:
                logger.warning(
                    "No progress in pagination; breaking to prevent loop."
                )
                break
            new_to_date = oldest_timestamp - timedelta(
                minutes=timeframe.minutes
            )

            to_date = new_to_date

        logger.info(
            f"Total data points fetched: {len(all_data)}, iterations: {count}"
        )

        return all_data

    def get_ohlcv_data(
        self, pair: str, timeframe: Timeframe, start: datetime, end: datetime
    ) -> pd.DataFrame:
        data = self._ohlcv_warehouse.load_ohlcv_data(
            pair, timeframe, start, end
        )

        full_idx = pd.date_range(start, end, freq=timeframe.pandas_freq)
        missing_ts = full_idx.difference(data.index)
        gaps = self._timestamps_to_spans(missing_ts, timeframe.timedelta)

        if not gaps:
            return data

        for gap_start, gap_end in gaps:
            logger.debug(f"Filling gap for {pair}: {gap_start} -> {gap_end}")
            chunk = self._fetch_ohlcv_data(
                pair, timeframe, gap_start, gap_end
            )
            self._ohlcv_warehouse.store_ohlcv_data(
                pair=pair, timeframe=timeframe, data=chunk)

        return self._ohlcv_warehouse.load_ohlcv_data(
            pair, timeframe, start, end
        )
