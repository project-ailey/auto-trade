from datetime import datetime
from typing import List

from matplotlib.axes import Axes

from indicator.indicator_drawer import IndicatorDrawer


class VolumeIndicatorDrawer(IndicatorDrawer):
    def __init__(self):
        super().__init__(name=f"volume", color='black')

    def draw(self, symbol, timeframe: str, end_time: datetime, target_plot: Axes, indexes: List[int], candles, timestamps, opens, closes, lows, highs, volumes):
        for i in range(len(candles)):
            if end_time != None and candles[i].timestamp > end_time:
                break

            color = 'green' if closes[i] >= opens[i] else 'red'
            target_plot.plot([indexes[i], indexes[i]], [0, volumes[i]], color=color, linewidth=3)

        target_plot.set_ylabel('Volume')
        # target_plot.set_xlabel('Time')
        # target_plot.set_title('Volume')
        target_plot.grid(True)
