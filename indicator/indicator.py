from abc import ABC, abstractmethod

# Abstract base class for indicators
class Indicator(ABC):
    def __init__(self, name: str):
        self.name = name

    # Calculate indicator and store in candles
    @abstractmethod
    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        pass