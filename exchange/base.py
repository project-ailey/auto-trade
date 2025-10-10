from typing import List, Dict
from datetime import datetime
import random

class BaseExchange:

    def get_market_time(self):
        return (0, 0, 0, 0, 0, 0)   # market_start_hour / minute, regular_market_start_hour / minute, regular_market_end_hour / minute

    # Fetch candle data and return as a standardized dictionary format
    def fetch_candles(self, symbol: str, timeframe: str, limit: int, excd: str = None) -> List[Dict[str, float]]:
        base_time = datetime.now()
        candles = []

        # default values
        for i in range(limit):
            timestamp = (base_time.replace(minute=base_time.minute - i)).timestamp() * 1000
            open_price = 10000 + i * 10 + random.uniform(-5, 5)
            close_price = open_price + random.uniform(-5, 5)
            low_price = min(open_price, close_price) - random.uniform(0, 5)
            high_price = max(open_price, close_price) + random.uniform(0, 5)
            volume = random.uniform(100, 200)
            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
        return candles[::-1]

    # Convert timeframe string to seconds
    def _timeframe_to_seconds(self, timeframe: str) -> int:
        units = {"m": 60, "h": 3600, "d": 86400, "w": 604800, "M": 2592000}  # week, month added
        num = int(''.join(filter(str.isdigit, timeframe)))
        unit = ''.join(filter(str.isalpha, timeframe))
        return num * units.get(unit, 60)  # default is minutes

    def fetch_tickers(self):
        return None
