
import pytest
from unittest.mock import MagicMock

from src.manager import OHLCVManager


@pytest.fixture
def ohlcv_manager(monkeypatch):
    fake_api = MagicMock(name="MoralisAPI")
    fake_warehouse = MagicMock(name="OHLCVWarehouse")
    manager = OHLCVManager(fake_api, fake_warehouse)
    return manager, fake_api, fake_warehouse


class TestTimestampsToSpans:
    @pytest.mark.skip
    def test_no_gap(self, ohlcv_manager):
        pass

    @pytest.mark.skip
    def test_single_gap(self, ohlcv_manager):
        pass

    @pytest.mark.skip
    def test_multiple_gaps(self, ohlcv_manager):
        pass

    @pytest.mark.skip
    def test_no_data(self, ohlcv_manager):
        pass


class TestToUTC:
    pass


class TestFetchOHLCVData:
    pass


class TestGetOHLCVData:
    @pytest.mark.skip
    def test_full_data(self):
        pass

    @pytest.mark.skip
    def test_no_data(self):
        pass

    @pytest.mark.skip
    def test_partial_data(self):
        pass
