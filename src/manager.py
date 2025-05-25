
from .warehouse import OHLCVWarehouse
from .moralis_api import MoralisAPI


class OHLCVManager:
    def __init__(
        self,
        moralis_api: MoralisAPI = MoralisAPI(),
        ohlcv_warehouse: OHLCVWarehouse = OHLCVWarehouse()
    ):
        pass
