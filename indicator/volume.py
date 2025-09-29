from typing import List

from matplotlib.axes import Axes
from numpy import float64

from candle import Candle
from indicator.indicator_drawer import IndicatorDrawer


class VolumeIndicatorDrawer(IndicatorDrawer):
    def __init__(self):
        super().__init__(name=f"volume", color='black')

    def draw(self, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes, candles: List[Candle]):
        smas = [c.get_indicator(self.name) for c in candles]

        for i in range(len(candles)):
            color = 'green' if closes[i] >= opens[i] else 'red'
            target_plot.plot([indexes[i], indexes[i]], [0, volumes[i]], color=color, linewidth=3)

        target_plot.set_ylabel('Volume')
        # target_plot.set_xlabel('Time')
        # target_plot.set_title('Volume')
        target_plot.grid(True)
