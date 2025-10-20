from typing import List

from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineOnewayIndicator(TrendLineIndicator):
    def __init__(self, trend_atr_multiplier: float = 2):
        super().__init__(trend_type="oneway", trend_atr_multiplier=trend_atr_multiplier)

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        # calculate swing trend
        base_candle = candles[0]

        # Based on the first candle, determine the direction unconditionally. Doji is treated as bearish.
        self.set_swing_dir(base_candle, TrendLineIndicator.UP if base_candle.is_bullish() else TrendLineIndicator.DOWN)
        self.set_swing_price(base_candle, base_candle.low if base_candle.is_bullish() else base_candle.high)

        for i in range(1, len(candles)):
            curr_candle = candles[i]

            if self.get_swing_dir(base_candle) == TrendLineIndicator.UP:  # if base candle is in an uptrend
                if curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, switch to downtrend (change base candle)

                    self.set_swing_dir(curr_candle, TrendLineIndicator.DOWN)
                    self.set_swing_price(base_candle, base_candle.high)
                    self.set_swing_dir(base_candle, TrendLineIndicator.TOP) # peak

                    base_candle = curr_candle
                elif curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, maintain uptrend (change base candle)
                    self.set_swing_dir(curr_candle, TrendLineIndicator.UP)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        self.set_swing_price(base_candle, base_candle.high)

                    self.set_swing_dir(curr_candle, TrendLineIndicator.ENGULFED_IN_UP) # if contained within base candle’s high/low, keep uptrend (no base change)

            elif self.get_swing_dir(base_candle) == TrendLineIndicator.DOWN:  # if base candle is in a downtrend
                if curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, switch to uptrend (change base candle)
                    self.set_swing_dir(curr_candle, TrendLineIndicator.UP)
                    self.set_swing_price(base_candle, base_candle.low)
                    self.set_swing_dir(base_candle, TrendLineIndicator.BOTTOM) # bottom

                    base_candle = curr_candle
                elif curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, maintain downtrend (change base candle)
                    self.set_swing_dir(curr_candle, TrendLineIndicator.DOWN)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        self.set_swing_price(base_candle, base_candle.low)

                    self.set_swing_dir(curr_candle, TrendLineIndicator.ENGULFED_IN_DOWN)  # if contained within base candle’s high/low, keep downtrend (no base change)

            else:
                print('error')

class TrendLineOnewayIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('oneway', swing_color, major_swing_color, trend_color)