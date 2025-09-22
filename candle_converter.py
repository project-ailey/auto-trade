from datetime import datetime
from typing import List, Dict
from candle import Candle

class CandleConverter:

    # Convert standardized dictionary data into a list of Candle objects
    def to_candles(self, data: List[Dict[str, float]]) -> List[Candle]:
        candles = []
        for entry in data:
            candle = Candle(
                timestamp=datetime.fromtimestamp(entry["timestamp"] / 1000),
                open_price=float(entry["open"]),
                close_price=float(entry["close"]),
                low_price=float(entry["low"]),
                high_price=float(entry["high"]),
                volume=float(entry["volume"])
            )
            candles.append(candle)
        return candles
