from datetime import datetime

class Candle:
    def __init__(self, timestamp: datetime, open_price: float, close_price: float,
                 low_price: float, high_price: float, volume: float = 0.0):
        self.timestamp = timestamp
        self.open = open_price
        self.close = close_price
        self.low = low_price
        self.high = high_price
        self.volume = volume
        self.indicators = {}  # Dictionary to store indicator values

    # Set indicator value
    def set_indicator(self, name: str, value: float):
        self.indicators[name] = value

    # Get indicator value
    def get_indicator(self, name: str) -> float | None:
        return self.indicators.get(name)

    def is_bullish(self):
        return self.open < self.close

    def is_bearish(self):
        return self.open > self.close

    def is_doji(self):
        return self.open == self.close

    def __str__(self) -> str:
        return (f"Candle(timestamp={self.timestamp}, open={self.open}, "
                f"close={self.close}, low={self.low}, high={self.high}, "
                f"volume={self.volume}, is_uptrend={self.is_uptrend}, indicators={self.indicators})")
