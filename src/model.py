
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel


class OHLCVData(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
