from abc import ABC, abstractmethod
from datetime import datetime

# Abstract base class for indicators
class Indicator(ABC):
    def __init__(self, name: str):
        self.name = name

    # Calculate indicator and store in candles
    @abstractmethod
    def calculate(self, symbol, timeframe: str, end_time: datetime, candles, timestamps, opens, closes, lows, highs, volumes) -> None:
        pass