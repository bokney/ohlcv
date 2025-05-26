
import os
import json
import pytest
import requests
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, Mock

from src.moralis_api import MoralisAPI
from src.timeframe import Timeframe
from src.model import OHLCVData

BASE_MOCK_DIR = os.path.join(os.path.dirname(__file__), "mock_data")


@pytest.fixture(autouse=True)
def patch_moralis_api_key(monkeypatch):
    monkeypatch.setattr("src.config.Config.moralis_api_key", "dummy_api_key")


@pytest.fixture
def mock_moralis_api():
    return MoralisAPI()


@pytest.fixture
def moralis_response_response_1():
    path = os.path.join(BASE_MOCK_DIR, "sample_ohlcv_page1.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def mock_requests_get(moralis_response_response_1):
    mock_response = Mock()
    mock_response.json.return_value = moralis_response_response_1
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        yield mock_response


class TestGetOHLCVData:
    @patch("src.backoff.sleep", return_value=None)
    def test_successful_response(
        self, mock_sleep, mock_moralis_api, moralis_response_response_1
    ):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = moralis_response_response_1
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = mock_moralis_api.get_ohlcv_data(
                pair_address=pair_address,
                timeframe=timeframe,
                currency=currency,
                from_date=from_date,
                to_date=to_date
            )

        assert result
        assert isinstance(result, list)
        assert isinstance(result[0], OHLCVData)

    @patch("src.backoff.sleep", return_value=None)
    def test_non_200_response(self, mock_sleep, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("404 Client Error")
        )

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError):
                mock_moralis_api.get_ohlcv_data(
                    pair_address=pair_address,
                    timeframe=timeframe,
                    currency=currency,
                    from_date=from_date,
                    to_date=to_date
                )

    @patch("src.backoff.sleep", return_value=None)
    def test_request_exception(self, mock_sleep, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        with patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException("Network Error")
        ):
            with pytest.raises(requests.exceptions.RequestException):
                mock_moralis_api.get_ohlcv_data(
                    pair_address=pair_address,
                    timeframe=timeframe,
                    currency=currency,
                    from_date=from_date,
                    to_date=to_date
                )

    def test_malformed_json(self, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = ValueError("Malformed JSON")

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(ValueError):
                mock_moralis_api.get_ohlcv_data(
                    pair_address=pair_address,
                    timeframe=timeframe,
                    currency=currency,
                    from_date=from_date,
                    to_date=to_date
                )

    def test_missing_fields_in_entry(self, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        sample_data = {
            "result": [
                {
                    "timestamp": "2024-04-20T20:00:00",
                    "open": "1.0",
                    "high": "2.0",
                    "low": "0.5",
                    "close": "1.5",
                    "volume": "100.0"
                }, {
                    "timestamp": "2024-04-20T21:00:00",
                    # "open" is missing here
                    "high": "2.1",
                    "low": "0.6",
                    "close": "1.6",
                    "volume": "110.0"
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = sample_data

        with patch("requests.get", return_value=mock_response):
            result = mock_moralis_api.get_ohlcv_data(
                pair_address=pair_address,
                timeframe=timeframe,
                currency=currency,
                from_date=from_date,
                to_date=to_date
            )

        assert len(result) == 1, "Only one valid entry should be processed"

    def test_improper_data_format(self, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        sample_data = {
            "result": [
                {
                    "timestamp": "invalid-timestamp",
                    "open": "1.0",
                    "high": "2.0",
                    "low": "0.5",
                    "close": "1.5",
                    "volume": "100.0"
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = sample_data

        with patch("requests.get", return_value=mock_response):
            result = mock_moralis_api.get_ohlcv_data(
                pair_address=pair_address,
                timeframe=timeframe,
                currency=currency,
                from_date=from_date,
                to_date=to_date
            )

        assert result == [], (
            "Entries with invalid data formats should be skipped."
        )

    def test_partial_record_processing(
        self, mock_moralis_api, moralis_response_response_1
    ):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        valid_entry = {
            "timestamp": "2024-04-20T20:00:00",
            "open": "1.0",
            "high": "2.0",
            "low": "0.5",
            "close": "1.5",
            "volume": "100.0"
        }

        invalid_entry = {
            "timestamp": "2024-04-20T21:00:00",
            "open": "1.1",
            "high": "2.1",
            "low": "0.6",
            "close": "not-a-number",
            "volume": "110.0"
        }

        sample_data = {"result": [valid_entry, invalid_entry]}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = sample_data

        with patch("requests.get", return_value=mock_response):
            result = mock_moralis_api.get_ohlcv_data(
                pair_address=pair_address,
                timeframe=timeframe,
                currency=currency,
                from_date=from_date,
                to_date=to_date
            )

        assert len(result) == 1, "Only one valid entry should be returned."

        assert result[0].open == Decimal("1.0")
        assert result[0].timestamp == datetime.fromisoformat(
            valid_entry["timestamp"]
        )

    def test_empty_data_set(self, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"
        from_date = datetime(2024, 4, 20, 19, 0, 0)
        to_date = datetime(2024, 4, 20, 23, 30, 0)

        sample_data = {"result": []}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = sample_data

        with patch("requests.get", return_value=mock_response):
            result = mock_moralis_api.get_ohlcv_data(
                pair_address=pair_address,
                timeframe=timeframe,
                currency=currency,
                from_date=from_date,
                to_date=to_date
            )

        assert result == [], "Expected empty list if there are no results."

    def test_boundary_timestamps(self, mock_moralis_api):
        pair_address = "dummy_pair"
        timeframe = Timeframe.MIN5
        currency = "usd"

        from_date = datetime(1970, 1, 1, 0, 0, 0)
        to_date = datetime(2100, 12, 31, 23, 59, 59)

        sample_data = {"result": []}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = sample_data

        with patch("requests.get", return_value=mock_response):
            with patch("requests.Request.prepare") as mock_prepare:
                dummy_prepared = Mock()

                def fake_prepare():
                    dummy_prepared.url = (
                        f"https://example.com"
                        f"?fromDate={from_date.isoformat()}"
                        f"&toDate={to_date.isoformat()}"
                    )
                    return dummy_prepared
                mock_prepare.side_effect = fake_prepare

                mock_moralis_api.get_ohlcv_data(
                    pair_address=pair_address,
                    timeframe=timeframe,
                    currency=currency,
                    from_date=from_date,
                    to_date=to_date
                )

                url = dummy_prepared.url
                assert from_date.isoformat() in url, (
                    "fromDate parameter missing or incorrect in URL."
                )
                assert to_date.isoformat() in url, (
                    "toDate parameter missing or incorrect in URL."
                )
