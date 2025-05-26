
import os
import threading
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Config:
    _instance = None
    _lock = threading.Lock()
    MORALIS_API_KEY: str = "MORALIS_API_KEY"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def moralis_api_key(self) -> Optional[str]:
        value = os.getenv(self.MORALIS_API_KEY)
        if value is None:
            logger.error(
                "Missing required environment variable: "
                f"{self.MORALIS_API_KEY}"
            )
            raise OSError(
                "Missing required environment variable: "
                f"{self.MORALIS_API_KEY}"
            )
        logger.debug(f"{self.MORALIS_API_KEY} successfully retrieved.")
        return value
