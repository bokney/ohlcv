
import pytest
from datetime import timedelta
from ohlcv.timeframe import Timeframe


class TestTimeframe:
    def test_timeframe_minutes(self):
        assert Timeframe.S1.minutes == 1/60
        assert Timeframe.MIN1.minutes == 1
        assert Timeframe.H1.minutes == 60

    def test_timedelta_property(self):
        assert Timeframe.MIN5.timedelta == timedelta(minutes=5)
        assert Timeframe.D1.timedelta == timedelta(minutes=1440)

    @pytest.mark.parametrize("tf, expected", [
        (Timeframe.S1,   "1S"),
        (Timeframe.S10,  "10S"),
        (Timeframe.S30,  "30S"),
        (Timeframe.MIN1, "1T"),
        (Timeframe.MIN5, "5T"),
        (Timeframe.MIN10,"10T"),
        (Timeframe.MIN30,"30T"),
        (Timeframe.H1,   "1H"),
        (Timeframe.H4,   "4H"),
        (Timeframe.H12,  "12H"),
        (Timeframe.D1,   "1D"),
        (Timeframe.W1,   "1W"),
        (Timeframe.M1,   "1M"),
    ])
    def test_pandas_freq_property(self, tf, expected):
        assert tf.pandas_freq == expected
