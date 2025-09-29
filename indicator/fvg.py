from typing import List, Dict
from matplotlib.axes import Axes
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from indicator.indicator import Indicator
from candle import Candle
from indicator.indicator_drawer import IndicatorDrawer
from numpy import float64

from indicator.trendline_base import TrendLineIndicator


class FVGIndicator(Indicator):
    def __init__(self, ref_trend_type: str, atr_multiplier: float = 1.0) -> None:
        super().__init__(name="fvg")

        self.ref_trend_type = ref_trend_type
        self.atr_multiplier = atr_multiplier

    def calculate(self, candles: List[Candle]) -> None:
        raws: List[Dict] = []
        n = len(candles)

        # find gaps.
        for i in range(2, n):
            center_idx = i - 1
            prev, center, post = candles[i-2], candles[center_idx], candles[i]

            new_item = None
            if post.low > prev.high and center.is_bullish():
                prev_top = TrendLineIndicator.get_prev_swing_high('zigzag', center_idx, candles)
                if prev_top != None:
                    if center.close > candles[prev_top].high:
                        new_item = {"start": center.timestamp, "low": prev.high, "high": post.low, "color": 'teal',
                                    "index": center_idx}

            elif post.high < prev.low and center.is_bearish():
                prev_bottom = TrendLineIndicator.get_prev_swing_low('zigzag', center_idx, candles)
                if prev_bottom != None:
                    if center.close < candles[prev_bottom].low:
                        new_item = {"start": center.timestamp, "low": post.high, "high": prev.low, "color": 'tomato', "index": center_idx}

            if new_item != None:
                atr_val = candles[center_idx].get_indicator('atr') or 0
                if (new_item.get('high') - new_item.get('low')) >= atr_val * self.atr_multiplier:   # allow only above threshold
                    raws.append(new_item)


        for raw in raws:
            idx = raw.get('index')

            # End the FVG block when a candle body penetrates it
            is_filled = False
            for i in range(idx + 2, n):
                c = candles[i]
                body_low = min(c.open, c.close) # c.low
                body_high = max(c.open, c.close) # c.high

                is_bullish = raw.get('color') == 'teal'
                if ((is_bullish and body_low < raw.get('high')) or (is_bullish == False and body_high > raw.get('low'))):
                    is_filled = True
                    candles[idx].set_indicator('fvg_low', raw.get('low'))
                    candles[idx].set_indicator('fvg_high', raw.get('high'))
                    candles[idx].set_indicator('fvg_color', raw.get('color'))
                    candles[idx].set_indicator('fvg_until_idx', i)
                    break

            if is_filled == False:
                candles[idx].set_indicator('fvg_low', raw.get('low'))
                candles[idx].set_indicator('fvg_high', raw.get('high'))
                candles[idx].set_indicator('fvg_color', raw.get('color'))
                candles[idx].set_indicator('fvg_until_idx', None)

class FVGIndicatorDrawer(IndicatorDrawer):
    def __init__(self) -> None:
        super().__init__(name="fvg", color=None)

    def draw(self, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes, candles: List[Candle]):
        last_time = indexes[-1]

        for i in range(len(candles)):
            c = candles[i]
            if c.get_indicator('fvg_low') != None:
                start_num = i
                end_num = c.get_indicator('fvg_until_idx') or last_time

                width = end_num - start_num
                height = c.get_indicator('fvg_high') - c.get_indicator('fvg_low')
                rect = Rectangle((start_num, c.get_indicator('fvg_low')), width, height,
                                 facecolor=c.get_indicator('fvg_color'), edgecolor=None, alpha=0.3)
                target_plot.add_patch(rect)

