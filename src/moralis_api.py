
import logging
import requests
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Union, Dict

from .timeframe import Timeframe
from .backoff import backoff
from .model import OHLCVData
from .config import Config

logger = logging.getLogger(__name__)


class MoralisAPI:
    _BASE_URL = "https://solana-gateway.moralis.io/token/mainnet/pairs"
    _config: Config = Config()

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = self._config.moralis_api_key

    @backoff(delay=2, retries=4)
    def get_ohlcv_data(
        self,
        pair_address: str,
        timeframe: Timeframe,
        currency: str,
        from_date: datetime,
        to_date: datetime,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> List[OHLCVData]:
        tf_str: str = str(timeframe.value)
        url = f"{self._BASE_URL}/{pair_address}/ohlcv"
        params: Dict[str, Union[str, int, None]] = {
            "timeframe": tf_str,
            "fromDate": from_date.isoformat(),
            "toDate": to_date.isoformat(),
            "limit": limit,
            "currency": currency
        }
        if cursor:
            params["cursor"] = cursor

        headers = {"X-API-Key": self._api_key}

        req = requests.Request('GET', url, params=params, headers=headers)
        prepped = req.prepare()
        logger.debug(f"Request URL: {prepped.url}")

        logger.info(
            f"Fetching OHLCV data for {pair_address}, "
            f"timeframe: {tf_str}, "
            f"from {from_date} to {to_date}, "
            f"limit: {limit}, cursor: {cursor}"
        )

        try:
            response = requests.get(url, params=params, headers=headers)
            logger.debug(f"Status code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Response headers: {response.headers}")
                logger.error(f"Response text: {response.text}")
            else:
                logger.debug(f"Response headers: {response.headers}")
                logger.debug(f"Response text: {response.text}")

            response.raise_for_status()
            data = response.json(parse_float=Decimal)

            logger.info(
                f"Received OHLCV data, {len(data.get('result', []))} records."
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching OHLCV data: {e}")
            raise

        ohlcv_list = []
        for entry in data.get("result", []):
            try:
                ohlcv = OHLCVData(
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    open=Decimal(entry["open"]),
                    high=Decimal(entry["high"]),
                    low=Decimal(entry["low"]),
                    close=Decimal(entry["close"]),
                    volume=Decimal(entry["volume"])
                )
                ohlcv_list.append(ohlcv)

            except Exception as e:
                logger.error(f"Error processing entry {entry}: {e}")

        return ohlcv_list
