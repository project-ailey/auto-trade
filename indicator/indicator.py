from abc import ABC, abstractmethod
from typing import List
from candle import Candle

# Abstract base class for indicators
class Indicator(ABC):
    def __init__(self, name: str):
        self.name = name

    # Calculate indicator and store in candles
    @abstractmethod
    def calculate(self, candles: List[Candle]) -> None:
        pass
