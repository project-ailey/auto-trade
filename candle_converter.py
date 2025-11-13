from datetime import datetime
from typing import List, Dict
from model.candle import Candle


class CandleConverter:

    # Convert standardized dictionary data into a list of Candle objects
    def to_candles(self, data: List[Dict[str, any]]) -> List[Candle]:
        candles = []
        for i in range(len(data)):
            entry = data[i]

            candle = Candle(
                index=i,
                timestamp=entry["timestamp"],
                open_price=float(entry["open"]),
                close_price=float(entry["close"]),
                low_price=float(entry["low"]),
                high_price=float(entry["high"]),
                volume=float(entry["volume"])
            )
            candles.append(candle)
        return candles