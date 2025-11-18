from abc import abstractmethod
from datetime import datetime
from typing import List

from matplotlib.axes import Axes


class IndicatorDrawer:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    @abstractmethod
    def draw(self, symbol, timeframe: str, end_time: datetime, target_plot: Axes, indexes: List[int], candles, timestamps, opens, closes, lows, highs, volumes):
        pass