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

    def __repr__(self):
        d = self.timestamp.strftime("%y-%m-%d %H:%M")
        return f"date={d}, o={self.open}, c={self.close}, l={self.low}, h={self.high}, v={self.volume}, inds={self.indicators}"

    def __str__(self):
        d = self.timestamp.strftime("%y-%m-%d %H:%M")
        return f"date={d}, o={self.open}, c={self.close}, l={self.low}, h={self.high}, v={self.volume}, inds={self.indicators}"

    # Set indicator value
    def set_indicator(self, name: str, value):
        self.indicators[name] = value

    # Get indicator value
    def get_indicator(self, name: str):
        return self.indicators.get(name)

    def is_bullish(self):
        return self.open < self.close

    def is_bearish(self):
        return self.open > self.close

    def is_doji(self):
        return self.open == self.close
