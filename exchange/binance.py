from exchange.base import BaseExchange
from typing import List, Dict
import ccxt
import time

# Binance exchange implementation (using ccxt)
class BinanceExchange(BaseExchange):

    def __init__(self):
        self.api = ccxt.binance()  # Can use public data without API key

    # Fetch latest candle data from Binance
    def fetch_candles(self, symbol: str, timeframe: str, limit: int, excd: str = None) -> List[Dict[str, float]]:
        # Calculate start time going back 'limit' candles from current time
        timeframe_in_seconds = self._timeframe_to_seconds(timeframe)
        since = int(time.time() * 1000) - (limit * timeframe_in_seconds * 1000)  # in milliseconds

        # Pass 'since' as a separate argument, not as params
        raw_data = self.api.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        return [
            {
                "timestamp": float(entry[0]),
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5])
            }
            for entry in raw_data
        ]

    def fetch_tickers(self):
        return self.api.fetch_tickers()
