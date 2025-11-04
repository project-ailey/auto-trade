from typing import List

from indicator.trendline_const import TrendDir
from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineOnewayIndicator(TrendLineIndicator):
    def __init__(self, trend_atr_multiplier: float = 2):
        super().__init__(trend_type="oneway", trend_atr_multiplier=trend_atr_multiplier)

    def calculate_swing_lines(self, symbol, timeframe) -> None:
        candles: List[Candle] = symbol.get_candles(timeframe)

        # calculate swing trend
        base_candle = candles[0]

        # Based on the first candle, determine the direction unconditionally. Doji is treated as bearish.
        base_candle.set_swing_dir(self.trend_type, TrendDir.UP if base_candle.is_bullish() else TrendDir.DOWN)
        base_candle.set_swing_price(self.trend_type, base_candle.low if base_candle.is_bullish() else base_candle.high)

        for i in range(1, len(candles)):
            curr_candle = candles[i]

            if self.get_swing_dir(base_candle) == TrendDir.UP:  # if base candle is in an uptrend
                if curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, switch to downtrend (change base candle)

                    curr_candle.set_swing_dir(self.trend_type, TrendDir.DOWN)
                    base_candle.set_swing_price(self.trend_type, base_candle.high)
                    base_candle.set_swing_dir(self.trend_type, TrendDir.TOP) # peak

                    base_candle = curr_candle
                elif curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, maintain uptrend (change base candle)
                    curr_candle.set_swing_dir(self.trend_type, TrendDir.UP)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_swing_price(self.trend_type, base_candle.high)

                    curr_candle.set_swing_dir(self.trend_type, TrendDir.ENGULFED_IN_UP) # if contained within base candle’s high/low, keep uptrend (no base change)

            elif base_candle.get_swing_dir(self.trend_type) == TrendDir.DOWN:  # if base candle is in a downtrend
                if curr_candle.high > base_candle.high:  # if the high is higher than the base candle’s high, switch to uptrend (change base candle)
                    curr_candle.set_swing_dir(self.trend_type, TrendDir.UP)
                    base_candle.set_swing_price(self.trend_type, base_candle.low)
                    base_candle.set_swing_dir(self.trend_type, TrendDir.BOTTOM) # 저점

                    base_candle = curr_candle
                elif curr_candle.low < base_candle.low:  # if the low is lower than the base candle’s low, maintain downtrend (change base candle)
                    curr_candle.set_swing_dir(self.trend_type, TrendDir.DOWN)
                    base_candle = curr_candle
                else:
                    if i == len(candles) - 1:
                        base_candle.set_swing_price(self.trend_type, base_candle.low)

                    curr_candle.set_swing_dir(self.trend_type, TrendDir.ENGULFED_IN_DOWN) # if contained within base candle’s high/low, keep downtrend (no base change)

            else:
                print('error')

class TrendLineOnewayIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('oneway', swing_color, major_swing_color, trend_color)