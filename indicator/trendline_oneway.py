from typing import List

from matplotlib.axes import Axes

from indicator.indicator import Indicator
from candle import Candle

from indicator.indicator_drawer import IndicatorDrawer
from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineOnewayIndicator(TrendLineIndicator):
    def __init__(self):
        super().__init__(trend_type="oneway")

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        # calculate swing trend
        base_candle = candles[0]

        swing_dir_indicator_name = "swing_dir_" + self.trend_type
        swing_price_indicator_name = "swing_price_" + self.trend_type

        # Based on the first candle, determine the direction unconditionally. Doji is treated as bearish.
        base_candle.set_indicator(swing_dir_indicator_name,
                                  TrendLineIndicator.UP if base_candle.is_bullish() else TrendLineIndicator.DOWN)
        base_candle.set_indicator(swing_price_indicator_name,
                                  base_candle.low if base_candle.is_bullish() else base_candle.high)

        for i in range(1, len(candles)):
            curr_candle = candles[i]

            if base_candle.get_indicator(swing_dir_indicator_name) == TrendLineIndicator.UP:  # if base candle is in an uptrend
                if curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, switch to downtrend (change base candle)
                    curr_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.DOWN)
                    base_candle.set_indicator(swing_price_indicator_name, base_candle.high)
                    base_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.TOP)  # peak

                    base_candle = curr_candle
                elif curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, maintain uptrend (change base candle)
                    curr_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.UP)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_indicator(swing_price_indicator_name, base_candle.high)
                    curr_candle.set_indicator(swing_dir_indicator_name,
                                              TrendLineIndicator.ENGULFED_IN_UP)  # if contained within base candle’s high/low, keep uptrend (no base change)

            elif base_candle.get_indicator(swing_dir_indicator_name) == TrendLineIndicator.DOWN:  # if base candle is in a downtrend
                if curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, switch to uptrend (change base candle)
                    curr_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.UP)
                    base_candle.set_indicator(swing_price_indicator_name, base_candle.low)
                    base_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.BOTTOM)  # bottom

                    base_candle = curr_candle
                elif curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, maintain downtrend (change base candle)
                    curr_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.DOWN)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_indicator(swing_price_indicator_name, base_candle.low)

                    curr_candle.set_indicator(swing_dir_indicator_name, TrendLineIndicator.ENGULFED_IN_DOWN)  # if contained within base candle’s high/low, keep downtrend (no base change)

            else:
                print('error')

class TrendLineOnewayIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, color: str, swing_color: str):
        super().__init__('oneway', color, swing_color)
