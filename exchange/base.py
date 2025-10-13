from typing import List, Dict
from datetime import datetime, timedelta
import random

from exchange.util import timeframe_to_seconds, find_regular_market_candle_time_before, timeframe_to_minutes


class BaseExchange:

    def get_market_time(self):
        return (0, 0, 0, 0, 0, 0)   # market_start_hour / minute, regular_market_start_hour / minute, regular_market_end_hour / minute

    def fetch_candles(self, ticker: str, timeframe: str, since: datetime, excd: str = None) -> List[Dict[str, float]]:
        candles = []

        curr = find_regular_market_candle_time_before(self, timeframe, since)
        i = 0
        while True:
            timestamp = curr
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

            if curr < since:
                break
            curr -= timedelta(minutes=timeframe_to_minutes(timeframe))
            i += 1

        return candles

    def fetch_tickers(self):
        return None