from typing import List
from indicator.indicator import Indicator
from model.candle import Candle
from indicator.indicator_drawer import IndicatorDrawer
from matplotlib.axes import Axes
import numpy as np

from model.symbol import Symbol


class MAIndicator(Indicator):
    def __init__(self, period: int = 14, mode: str = "sma") -> None:
        mode = mode.lower()
        if mode not in ("sma", "ema"): raise ValueError("mode must be 'sma' or 'ema'")
        super().__init__(name=f"ma_{period}")
        self.period = period
        self.mode = mode
        if self.mode == "ema": self.k = 2 / (self.period + 1)

    def calculate(self, symbol, timeframe: str) -> None:
        candles = symbol.get_candles(timeframe)

        n = len(candles)
        if n < self.period:
            for c in candles: c.set_indicator(self.name, None)
            return
        closes = [c.close for c in candles]
        ma_values: List[float | None] = [None] * n
        if self.mode == "sma":
            for i in range(n): ma_values[i] = None if i < self.period - 1 else sum(closes[i-self.period+1:i+1]) / self.period
        else:
            ma_values[self.period-1] = sum(closes[:self.period]) / self.period
            for i in range(self.period, n): prev = ma_values[i-1]; ma_values[i] = (closes[i] - prev) * self.k + prev
        for i, candle in enumerate(candles): candle.set_indicator(self.name, ma_values[i])

# Drawer class for MAIndicator
class MAIndicatorDrawer(IndicatorDrawer):
    def __init__(self, period: int = 14, color: str = 'blue', linewidth: float = 1.5) -> None:
        super().__init__(name=f"ma_{period}", color=color)
        self.linewidth = linewidth

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        vals = [c.get_indicator(self.name) for c in candles]
        arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
        target_plot.plot(indexes, arr, label=self.name.upper(), linewidth=self.linewidth, linestyle='-', color=self.color)
        target_plot.set_ylabel(self.name.upper()); target_plot.set_xlabel('Time'); target_plot.legend(); target_plot.grid(True)
