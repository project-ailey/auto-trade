from typing import List, Dict
from matplotlib.axes import Axes
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from indicator.indicator import Indicator
from candle import Candle
from indicator.indicator_drawer import IndicatorDrawer
from numpy import float64

class FVGIndicator(Indicator):
    def __init__(self, atr_multiplier: float = 1.0) -> None:
        super().__init__(name="fvg")
        self.atr_multiplier = atr_multiplier
        self.gaps: List[Dict] = []  # filtered, grouped gaps

    def calculate(self, candles: List[Candle]) -> None:
        raws: List[Dict] = []
        n = len(candles)

        # find gaps.
        for i in range(2, n):
            prev, center, post = candles[i-2], candles[i-1], candles[i]
            if post.low > prev.high:
                raws.append({"start": center.timestamp, "low": prev.high, "high": post.low, "color": 'teal', "index": i-1})
            elif post.high < prev.low:  # Bearish
                raws.append({"start": center.timestamp, "low": post.high, "high": prev.low, "color": 'tomato', "index": i-1})

        # filter only significant gaps
        for raw in raws:
            idx = raw.get('index')
            atr_val = candles[idx].get_indicator('atr')
            if atr_val is None: continue
            if (raw.get('high') - raw.get('low')) >= atr_val * self.atr_multiplier: # allow only above threshold
                # end the fvg block when a candle body penetrates it
                is_filled = False
                for i in range(idx + 2, n):
                    c = candles[i]
                    body_low = min(c.open, c.close)
                    body_high = max(c.open, c.close)
                    if body_high > raw.get('low') and body_low < raw.get('high'):
                        is_filled = True
                        candles[idx].set_indicator('fvg_low', raw.get('low'))
                        candles[idx].set_indicator('fvg_high', raw.get('high'))
                        candles[idx].set_indicator('fvg_color', raw.get('color'))
                        candles[idx].set_indicator('fvg_until', c.timestamp)
                        break

                if is_filled == False:
                    candles[idx].set_indicator('fvg_low', raw.get('low'))
                    candles[idx].set_indicator('fvg_high', raw.get('high'))
                    candles[idx].set_indicator('fvg_color', raw.get('color'))
                    candles[idx].set_indicator('fvg_until', None)

class FVGIndicatorDrawer(IndicatorDrawer):
    def __init__(self) -> None:
        super().__init__(name="fvg", color=None)

    def draw(self, target_plot: Axes, timestamps: List[float64], opens, closes, lows, highs, volumes, candles: List[Candle]) -> None:
        last_time = timestamps[-1]

        for c in candles:
            if c.get_indicator('fvg_low') != None:
                start_num = mdates.date2num(c.timestamp)
                end_time = c.get_indicator('fvg_until') or last_time
                end_num = mdates.date2num(end_time)
                width = end_num - start_num
                height = c.get_indicator('fvg_high') - c.get_indicator('fvg_low')
                rect = Rectangle((start_num, c.get_indicator('fvg_low')), width, height,
                                 facecolor=c.get_indicator('fvg_color'), edgecolor=None, alpha=0.3)
                target_plot.add_patch(rect)
