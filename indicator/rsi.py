from typing import List

from matplotlib.axes import Axes

from indicator.indicator import Indicator
from model.candle import Candle
from indicator.indicator_drawer import IndicatorDrawer
from model.symbol import Symbol

class RSIIndicator(Indicator):

    def __init__(self, period: int = 14):
        super().__init__(name="rsi")
        self.period = period

    def calculate(self, symbol, timeframe: str) -> None:
        candles = symbol.get_candles(timeframe)

        if len(candles) < self.period:
            for candle in candles:
                candle.set_indicator(self.name, None)
            return

        closes = [c.close for c in candles]

        # Calculate upward movement (U) and downward movement (D)
        gains = [0.0] * len(closes)
        losses = [0.0] * len(closes)
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            gains[i] = diff if diff > 0 else 0
            losses[i] = -diff if diff < 0 else 0

        # Calculate RSI
        for i in range(len(candles)):
            if i < self.period:
                candles[i].set_indicator(self.name, None)
                continue

            avg_gain = sum(gains[i - self.period + 1:i + 1]) / self.period
            avg_loss = sum(losses[i - self.period + 1:i + 1]) / self.period

            rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
            rsi = 100 - (100 / (1 + rs)) if rs != float('inf') else 100
            candles[i].set_indicator(self.name, rsi)

class RSIIndicatorDrawer(IndicatorDrawer):
    def __init__(self):
        super().__init__(name=f"rsi", color='black')

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        rsis = [c.get_indicator("rsi") for c in candles]

        # RSI plot (lower panel)
        target_plot.plot(indexes, rsis, 'm-', label='RSI')
        target_plot.axhline(70, color='red', linestyle='--', alpha=0.5)
        target_plot.axhline(30, color='green', linestyle='--', alpha=0.5)
        target_plot.set_ylim(0, 100)
        target_plot.set_ylabel('RSI')
        #target_plot.set_xlabel('Time')
        target_plot.legend()
        target_plot.grid(True)