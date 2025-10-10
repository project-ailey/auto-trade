from abc import abstractmethod
from typing import List

from matplotlib.axes import Axes

from model.candle import Candle

class IndicatorDrawer:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    @abstractmethod
    def draw(self, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes, candles: List[Candle]):
        pass