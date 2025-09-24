from typing import List

from matplotlib.axes import Axes

from indicator.indicator import Indicator
from candle import Candle
from numpy import float64

from indicator.indicator_drawer import IndicatorDrawer


class TrendLineIndicator(Indicator):
    NONE = 0
    UP = 1
    DOWN = 2
    TOP = 3
    BOTTOM = 4
    ENGULFED_IN_UP = 5,
    ENGULFED_IN_DOWN = 6,


    def __init__(self):
        super().__init__(name="trend_line")

    def calculate(self, candles: List[Candle]) -> None:
        if len(candles) == 0:
            return

        base_candle = candles[0]
        # Decide the direction based on the first candle. Doji is treated as bearish.
        base_candle.set_indicator("trend_dir", TrendLineIndicator.UP if base_candle.is_bullish() else TrendLineIndicator.DOWN)
        base_candle.set_indicator("trend_price", base_candle.low if base_candle.is_bullish() else base_candle.high)

        for i in range(1, len(candles)):
            curr_candle = candles[i]

            if base_candle.get_indicator("trend_dir") == TrendLineIndicator.UP:  # When the base candle is in an uptrend
                if curr_candle.low < base_candle.low:   # Low is lower than the base candle low, switch to downtrend (change base candle)
                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.DOWN)
                    base_candle.set_indicator("trend_price", base_candle.high)
                    base_candle.set_indicator("trend_dir", TrendLineIndicator.TOP) # Peak

                    base_candle = curr_candle
                elif curr_candle.high > base_candle.high:   # High is higher than the base candle high, keep uptrend (change base candle)
                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.UP)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_indicator("trend_price", base_candle.high)
                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.ENGULFED_IN_UP)   # If engulfed within base candle high and low, keep uptrend (do not change base candle)

            elif base_candle.get_indicator("trend_dir") == TrendLineIndicator.DOWN: # When the base candle is in a downtrend
                if curr_candle.high > base_candle.high:   # High is higher than the base candle high, switch to uptrend (change base candle)
                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.UP)
                    base_candle.set_indicator("trend_price", base_candle.low)
                    base_candle.set_indicator("trend_dir", TrendLineIndicator.BOTTOM)   # Bottom

                    base_candle = curr_candle
                elif curr_candle.low < base_candle.low:   # Low is lower than the base candle low, keep downtrend (change base candle)
                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.DOWN)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_indicator("trend_price", base_candle.low)

                    curr_candle.set_indicator("trend_dir", TrendLineIndicator.ENGULFED_IN_DOWN)   # If engulfed within base candle high and low, keep downtrend (do not change base candle)

            else:
                print ('error')

class TrendLineIndicatorDrawer(IndicatorDrawer):
    def __init__(self, color: str):
        super().__init__('trend_price', color)

    def get_previous_trend_peak(self, current_index: int, candles: List[Candle]):
        for i in range(current_index, -1, -1):
            if candles[i].get_indicator('trend_dir') == TrendLineIndicator.TOP:
                return candles[i]
        return None

    def draw(self, target_plot: Axes, timestamps: List[float64], opens, closes, lows, highs, volumes, candles: List[Candle]):
        trend_prices = [c.get_indicator("trend_price") for c in candles]

        trend_points = []
        for i in range(0, len(candles)):
            if trend_prices[i]:
                trend_points.append((timestamps[i], trend_prices[i]))

        if trend_points:
            trend_times, trend_vals = zip(*trend_points)
            target_plot.plot(trend_times, trend_vals, 'b--', label='Trend Line')
