from datetime import datetime
from typing import List
from indicator.indicator import Indicator
from indicator.ma import MAIndicator
from indicator.indicator_drawer import IndicatorDrawer
from matplotlib.axes import Axes
import numpy as np

# Implements a moving average indicator (mode='sma' or 'ema')
class MADailyIndicator(Indicator):
    def __init__(self, period: int = 14, mode: str = "sma") -> None:
        mode = mode.lower()
        if mode not in ("sma", "ema"): raise ValueError("mode must be 'sma' or 'ema'")
        super().__init__(name=f"ma_daily_{period}")
        self.period = period
        self.mode = mode
        if self.mode == "ema": self.k = 2 / (self.period + 1)

    def calculate(self, symbol, timeframe: str, end_time: datetime, candles, timestamps, opens, closes, lows, highs, volumes) -> None:
        if timeframe == "1d":   # Skip if the timeframe is 1d.
            return

        n = len(candles)
        if n < self.period:
            for c in candles: c.set_indicator(self.name, None)
            return

        # Pre-calculate the daily moving average.
        candles_1d = symbol.get_candles("1d", None) # todo. None temporarily. Need fix
        if not candles_1d:
            return

        timestamp_1d = [c.timestamp for c in candles_1d]
        closes_1d = [c.close for c in candles_1d]
        ma_values_1d = MAIndicator.calculate_moving_averages(self.mode, self.period, closes_1d)

        candle_table = {}
        for i in range(len(timestamp_1d)):
            candle_table[int(timestamp_1d[i].timestamp())] = ma_values_1d[i]

        # Assign the corresponding daily MA to each date.
        for i in range(n):
            this_day = datetime(candles[i].timestamp.year, candles[i].timestamp.month, candles[i].timestamp.day)
            if int(this_day.timestamp()) in candle_table:
                candles[i].set_indicator(self.name, candle_table[int(this_day.timestamp())])    # Insert the pre-calculated MA value.

# Drawing class for MAIndicator
class MADailyIndicatorDrawer(IndicatorDrawer):
    def __init__(self, period: int = 14, color: str = 'blue', linewidth: float = 1.5) -> None:
        super().__init__(name=f"ma_daily_{period}", color=color)
        self.linewidth = linewidth

    def draw(self, symbol, timeframe: str, end_time: datetime, target_plot: Axes, indexes: List[int], candles, timestamps, opens, closes, lows, highs, volumes):
        vals = [c.get_indicator(self.name) for c in candles]
        arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
        target_plot.plot(indexes, arr, label=self.name.upper(), linewidth=self.linewidth, linestyle='-', color=self.color)
        target_plot.set_ylabel(self.name.upper()); target_plot.set_xlabel('Time'); target_plot.legend(); target_plot.grid(True)
