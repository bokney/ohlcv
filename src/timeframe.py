
from enum import Enum
from datetime import timedelta

class Timeframe(Enum):
    S1 = ("1s", 1/60)
    S10 = ("10s", 10/60)
    S30 = ("30s", 30/60)
    MIN1 = ("1min", 1)
    MIN5 = ("5min", 5)
    MIN10 = ("10min", 10)
    MIN30 = ("30min", 30)
    H1 = ("1h", 60)
    H4 = ("4h", 240)
    H12 = ("12h", 720)
    D1 = ("1d", 1440)
    W1 = ("1w", 10080)
    M1 = ("1m", 43200)

    def __new__(cls, label, minutes):
        obj = object.__new__(cls)
        obj._value_ = label
        obj.minutes = minutes
        return obj

    @property
    def timedelta(self) -> timedelta:
        return timedelta(minutes=self.minutes)

    @property
    def pandas_freq(self) -> str:
        label = self.value.lower()
        if label.endswith("s"):
            return label.upper()
        if label.endswith("min"):
            return f"{int(self.minutes)}T"
        unit = label[-1].upper()
        qty = label[:-1]
        return f"{qty}{unit}"
