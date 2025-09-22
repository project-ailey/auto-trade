from abc import abstractmethod
from typing import List
from candle import Candle

class IndicatorDrawer:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    @abstractmethod
    def draw(self, target_plot, timestamps, opens, closes, lows, highs, volumes, candles: List[Candle]) -> None:
        pass