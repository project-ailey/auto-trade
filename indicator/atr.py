from typing import List
from matplotlib.axes import Axes
import numpy as np

from indicator.indicator import Indicator
from model.candle import Candle
from indicator.indicator_drawer import IndicatorDrawer
from model.symbol import Symbol

# ATR (Average True Range) indicator implementation
# mode="sma" for simple moving average ATR,
# mode="ema" for Wilder's EMA smoothing ATR.
class ATRIndicator(Indicator):
    def __init__(self, period: int = 14, mode: str = "sma") -> None:
        mode = mode.lower()
        if mode not in ("sma", "ema"): raise ValueError("mode must be 'sma' or 'ema'")
        super().__init__(name="atr")
        self.period = period
        self.mode = mode

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        n = len(candles)
        min_required = self.period if self.mode == "sma" else self.period + 1
        if n < min_required:
            for c in candles: c.set_indicator(self.name, None)
            return

        # calculate tr
        tr: List[float] = [0.0] * n
        for i in range(n):
            high, low = candles[i].high, candles[i].low
            tr[i] = (high - low) if i == 0 else max(
                high - low,
                abs(high - candles[i-1].close),
                abs(low  - candles[i-1].close)
            )

        # calculate atr
        atr_values: List[float | None] = [None] * n
        if self.mode == "sma":
            for i in range(n):
                atr_values[i] = None if i < self.period else sum(tr[i-self.period+1:i+1]) / self.period
        else:
            initial = sum(tr[1:self.period+1]) / self.period
            atr_values[self.period] = initial
            for i in range(self.period+1, n):
                atr_values[i] = (atr_values[i-1] * (self.period - 1) + tr[i]) / self.period

        for i, candle in enumerate(candles): candle.set_indicator(self.name, atr_values[i])


class ATRIndicatorDrawer(IndicatorDrawer):
    def __init__(self) -> None:
        super().__init__(name="atr", color='purple')

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        vals = [c.get_indicator(self.name) for c in candles]
        arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
        target_plot.plot(indexes, arr, label=self.name.upper(), linewidth=1.5, linestyle='-', color=self.color)
        target_plot.set_ylabel(self.name.upper())
        target_plot.set_xlabel('Time')
        target_plot.legend()
        target_plot.grid(True)
