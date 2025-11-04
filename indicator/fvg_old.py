from bisect import bisect_left, bisect_right, bisect
from datetime import datetime
from typing import List, Dict
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from indicator.indicator import Indicator
from indicator.trendline_const import TrendDir
from model.candle import Candle
from indicator.indicator_drawer import IndicatorDrawer


class FVGOldIndicator(Indicator):
    def __init__(self, trend_type: str, atr_multiplier: float = 1.0, ob_limit_on_trendline: int = 3) -> None:
        super().__init__(name="fvg")

        self.trend_type = trend_type
        self.atr_multiplier = atr_multiplier
        self.ob_limit_on_trendline = ob_limit_on_trendline

    def find_order_block(self, symbol, timeframe: str, fvg_idx: int, candles: List[Candle]):
        fvg_dir = TrendDir.UP if candles[fvg_idx].is_bullish() else TrendDir.DOWN

        prev_candle_idx = fvg_idx - 1
        if fvg_dir == TrendDir.UP:
            if candles[prev_candle_idx].is_bearish():
                # If the candle before the FVG is bearish, it’s an order block.
                return (prev_candle_idx, prev_candle_idx)
            else:
                # If the candle before the FVG is bullish, find a bearish candle.
                for i in range(prev_candle_idx - 1, -1, -1):
                    if candles[i].is_bearish():
                        start_idx = -1
                        if start_idx == -1:
                            return (i, i)
                        else:
                            return (start_idx, i)

        elif fvg_dir == TrendDir.DOWN:
            if candles[prev_candle_idx].is_bullish():
                # If the candle before the FVG is bullish, it’s an order block.
                return (prev_candle_idx, prev_candle_idx)
            else:
                # If the candle before the FVG is bearish, find a bullish candle.
                for i in range(prev_candle_idx - 1, -1, -1):
                    if candles[i].is_bullish():
                        start_idx = -1
                        if start_idx == -1:
                            return (i, i)
                        else:
                            return (start_idx, i)

        return (-1, -1)

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        raws: List[Dict] = []
        n = len(candles)

        ob_limit_table = {}
        for i in range(2, n):
            center_idx = i - 1
            prev, center, post = candles[i-2], candles[center_idx], candles[i]

            # if center.timestamp.strftime('%Y-%m-%d %H:%M') == '2025-01-15 12:00':
            #     print ('test')

            new_item = None
            prev_trend_point_idx = -1
            if post.low > prev.high and center.is_bullish():    # Uptrend
                prev_swing_low = symbol.get_prev_major_swing_low(timeframe, self.trend_type, center_idx)
                prev_trend_point_idx = prev_swing_low.index

                if prev_trend_point_idx not in ob_limit_table:
                    ob_limit_table[prev_trend_point_idx] = 0

                if ob_limit_table[prev_trend_point_idx] < self.ob_limit_on_trendline:
                    new_item = {"start": center.timestamp, "low": prev.high, "high": post.low, "color": 'teal', "dir": TrendDir.UP, "index": center_idx}

                    # Find order block
                    (start, end) = self.find_order_block(symbol, timeframe, center_idx, candles)
                    if start != -1 and end != -1:
                        (low, high) = symbol.find_high_and_low_between_candles(timeframe, start, end)

                        new_item["order_block"] = {"high": high, "low": low, "color": '#003F3F', "start_index": start, "end_index": end}


            elif post.high < prev.low and center.is_bearish():  # Downtrend
                prev_swing_high = symbol.get_prev_major_swing_high(timeframe, self.trend_type, center_idx)
                prev_trend_point_idx = prev_swing_high.index

                if prev_trend_point_idx not in ob_limit_table:
                    ob_limit_table[prev_trend_point_idx] = 0

                if ob_limit_table[prev_trend_point_idx] < self.ob_limit_on_trendline:
                    new_item = {"start": center.timestamp, "low": post.high, "high": prev.low, "color": 'tomato', "dir": TrendDir.DOWN, "index": center_idx}

                    # Find order block
                    (start, end) = self.find_order_block(symbol, timeframe, center_idx, candles)
                    if start != -1 and end != -1:
                        (low, high) = symbol.find_high_and_low_between_candles(timeframe, start, end)

                        new_item["order_block"] = {"high": high, "low": low, "color": '#7A261F', "start_index": start, "end_index": end}

            if new_item != None and prev_trend_point_idx != -1:
                atr_val = candles[center_idx].get_indicator('atr') or 0
                if (new_item.get('high') - new_item.get('low')) >= atr_val * self.atr_multiplier:   # Filter only significant gaps
                    ob_limit_table[prev_trend_point_idx] += 1

                    raws.append(new_item)

        # Final setup
        for raw in raws:
            idx = raw.get('index')

            ob_raw = raw.get('order_block')
            if ob_raw != None:
                ob_start_idx = ob_raw.get('start_index')
                ob_end_idx = ob_raw.get('end_index')

            is_filled = False
            is_filled_order_block = False
            for i in range(idx + 2, n):
                c = candles[i]
                body_low = min(c.open, c.close) # c.low
                body_high = max(c.open, c.close) # c.high

                is_bullish = raw.get('dir') == TrendDir.UP
                if (is_filled == False and ((is_bullish and body_low < raw.get('high')) or (is_bullish == False and body_high > raw.get('low')))):
                    is_filled = True
                    # Mark FVG block as 'until' – stop when candle body intersects
                    candles[idx].set_indicator('fvg', {'low':raw.get('low'), 'high': raw.get('high'), 'color': raw.get('color'), 'dir': raw.get('dir'), 'until_idx': i})

                if (ob_raw and is_filled_order_block == False and ((is_bullish and body_low < ob_raw.get('high')) or (is_bullish == False and body_high > ob_raw.get('low')))):
                    is_filled_order_block = True
                    # Mark OB block as 'until' – stop when candle body intersects
                    candles[ob_start_idx].set_indicator('fvg_ob', {'low': ob_raw.get('low'), 'high': ob_raw.get('high'), 'color': ob_raw.get('color'), 'dir': raw.get('dir'), 'end_index': ob_raw.get('end_index'), 'until_idx': i})

                if is_filled and is_filled_order_block: # Skip only when both are filled
                   break

            if is_filled == False:
                candles[idx].set_indicator('fvg',{'low': raw.get('low'), 'high': raw.get('high'), 'color': raw.get('color'), 'dir': raw.get('dir'), 'until_idx': None})

            if ob_raw:
                if is_filled_order_block == False:
                    candles[ob_start_idx].set_indicator('fvg_ob', {'low': ob_raw.get('low'), 'high': ob_raw.get('high'), 'color': ob_raw.get('color'), 'dir': raw.get('dir'), 'end_index': ob_raw.get('end_index'), 'until_idx': None})

                for i in range(ob_start_idx + 1, ob_end_idx + 1):
                    candles[i].set_indicator('fvg_ob_candle', {})   # Added for convenience for drawer

class FVGOldIndicatorDrawer(IndicatorDrawer):
    def __init__(self, is_draw_fvg = True, is_draw_ob = True) -> None:
        super().__init__(name="fvg", color=None)

        self.is_draw_fvg = is_draw_fvg
        self.is_draw_ob = is_draw_ob

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        last_time = indexes[-1]

        for i in range(len(candles)):
            c = candles[i]
            if self.is_draw_fvg and c.get_indicator('fvg') != None:
                start_num = i
                end_num = c.get_indicator('fvg')['until_idx'] or last_time

                width = end_num - start_num
                height = c.get_indicator('fvg')['high'] - c.get_indicator('fvg')['low']
                rect = Rectangle((start_num, c.get_indicator('fvg')['low']), width, height,
                                 facecolor=c.get_indicator('fvg')['color'], edgecolor=None, alpha=0.3)
                target_plot.add_patch(rect)

            elif self.is_draw_ob and c.get_indicator('fvg_ob') != None:
                start_num = i
                end_num = c.get_indicator('fvg_ob')['until_idx'] or last_time

                width = end_num - start_num
                height = c.get_indicator('fvg_ob')['high'] - c.get_indicator('fvg_ob')['low']
                rect = Rectangle((start_num, c.get_indicator('fvg_ob')['low']), width, height,
                                 facecolor=c.get_indicator('fvg_ob')['color'], edgecolor=None, alpha=0.3)

                target_plot.add_patch(rect)

        #self.draw_ltf(symbol, '15m', target_plot, timestamps)

    def draw_ltf(self, symbol, lower_timeframe: str, target_plot: Axes, ht_timestamps: List[datetime]):

        # 1) Load higher TF & lower TF candles
        candles_ltf = symbol.get_candles(lower_timeframe)

        # 2) Process FVGs in each lower timeframe candle
        for idx_ltf, c in enumerate(candles_ltf):
            fvg = c.get_indicator('fvg')
            if not fvg:
                continue

            # Calculate start/end timestamps
            start_ts = c.timestamp
            end_idx_ltf = fvg.get('until_idx', None)
            if end_idx_ltf is None or end_idx_ltf >= len(candles_ltf):
                end_idx_ltf = len(candles_ltf) - 1
            end_ts = candles_ltf[end_idx_ltf].timestamp

            # 3) Map to higher timeframe index (using bisect)
            x0 = bisect_left(ht_timestamps, start_ts)
            x1 = bisect_left(ht_timestamps, end_ts)
            width = max(1, x1 - x0)

            # 4) FVG height/position
            y0 = fvg['low']
            height = fvg['high'] - fvg['low']

            # 5) Add patch
            rect = Rectangle(
                (x0, y0),
                width, height,
                facecolor= "black" if fvg.get('dir') == TrendDir.UP else "white",
                edgecolor=None,
                alpha=0.5
            )
            target_plot.add_patch(rect)
