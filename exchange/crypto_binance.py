from datetime import datetime, timezone

from exchange.base import BaseExchange
from typing import List, Dict
import ccxt
import time

from exchange.util import timeframe_to_seconds, timeframe_to_minutes


class CryptoBinanceExchange(BaseExchange):

    def __init__(self):
        self.api = ccxt.binance()  # Can use public data without API key

    # Fetch latest candle data from Binance
    def fetch_candles(self, ticker: str, timeframe: str, since: datetime, excd: str = None) -> List[Dict[str, float]]:
        since_ms = int(since.timestamp() * 1000)  # in milliseconds

        # calculate limit
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        limit = int((now_ms - since_ms) / (timeframe_to_seconds(timeframe) * 1000)) + 1

        # Pass 'since' as a separate argument, not as params
        raw_data = self.api.fetch_ohlcv(ticker, timeframe, since=since_ms, limit=limit)
        result = [
            {
                "timestamp": datetime.fromtimestamp(float(entry[0]) / 1000, tz=timezone.utc),
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5])
            }
            for entry in raw_data
        ]

        return result

    def fetch_tickers(self):
        return self.api.fetch_tickers()
