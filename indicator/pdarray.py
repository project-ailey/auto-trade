from typing import List
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from indicator.indicator import Indicator
from indicator.trendline_const import TrendDir
from indicator.indicator_drawer import IndicatorDrawer


class PDArrayIndicator(Indicator):
    def __init__(self, trend_type: str, atr_multiplier: float = 1.0, ob_limit_on_trendline: int = 3) -> None:
        super().__init__(name="fvg")

        self.trend_type = trend_type
        self.atr_multiplier = atr_multiplier
        self.ob_limit_on_trendline = ob_limit_on_trendline

    def find_order_block_internal(self, symbol, timeframe: str, offset_index: int, current_find_dir: int = 0, override_swing_dir: int = TrendDir.NONE):
        candles = symbol.get_candles(timeframe)

        swing_dir = candles[offset_index].get_major_swing_dir(self.trend_type) if current_find_dir == 0 else override_swing_dir   # for recursive
        price_dir = TrendDir.DOWN if swing_dir == TrendDir.TOP else TrendDir.UP
        ob_color = '#7A261F' if swing_dir == TrendDir.TOP else '#003F3F'

        if swing_dir == TrendDir.TOP:
            pass
        elif swing_dir == TrendDir.BOTTOM:
            pass
        else:
            return None

        if candles[offset_index].has_long_shadow(swing_dir == TrendDir.TOP, 1):
            # Rejection Block – When a long upper wick appears at the start of a down move
            if swing_dir == TrendDir.TOP:
                high = candles[offset_index].high
                low = max(candles[offset_index].open, candles[offset_index].close)
            else:
                high = min(candles[offset_index].open, candles[offset_index].close)
                low = candles[offset_index].low

            return {"high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

        else:
            if swing_dir == TrendDir.TOP:
                high = candles[offset_index].high
                low = max(candles[offset_index].open, candles[offset_index].close)
            else:
                high = min(candles[offset_index].open, candles[offset_index].close)
                low = candles[offset_index].low

            shadow_size = high - low
            if shadow_size > candles[offset_index].get_indicator('atr'):
                # Not a hammer or inverted hammer, but with a long wick
                return {"high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

            elif candles[offset_index].is_bullish() if swing_dir == TrendDir.TOP else candles[offset_index].is_bearish():
                # Order Block – When there is an order block at the swing point
                if candles[offset_index + 1].is_bullish() if swing_dir == TrendDir.TOP else candles[offset_index + 1].is_bearish():
                    low = candles[offset_index + 1].low
                    high = candles[offset_index + 1].high

                    return {"high": high, "low": low, "color": ob_color, "index": offset_index + 1, "dir": price_dir}
                else:
                    low = candles[offset_index].low
                    high = candles[offset_index].high

                    return {"high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

            else:
                # If there is no order block at the swing point, look before and after
                if current_find_dir == 0:
                    post_dir_ob = self.find_order_block_internal(symbol, timeframe, offset_index - 1, 1, swing_dir) # post has higher priority
                    prev_dir_ob = self.find_order_block_internal(symbol, timeframe, offset_index + 1, -1, swing_dir)  # If there's no post, check prev

                    if swing_dir == TrendDir.TOP:
                        if post_dir_ob != None and prev_dir_ob == None:
                            return post_dir_ob
                        elif post_dir_ob == None and prev_dir_ob != None:
                            return prev_dir_ob
                        else:
                            if post_dir_ob['high'] > prev_dir_ob['high']:
                                return post_dir_ob
                            else:
                                return prev_dir_ob

                elif current_find_dir == 1:
                    return self.find_order_block_internal(symbol, timeframe, offset_index - 1, 1, swing_dir)  # post has higher priority

                elif current_find_dir == -1:
                    return self.find_order_block_internal(symbol, timeframe, offset_index - 1, -1, swing_dir)  # post has higher priority

    def find_order_block(self, symbol, timeframe: str):
        curr_offset_index = 0

        result = []
        while True:
            next_swing_point = symbol.get_next_major_swing_point(timeframe, self.trend_type, curr_offset_index)
            if next_swing_point == None:
                break

            curr_offset_index = next_swing_point.index

            table = self.find_order_block_internal(symbol, timeframe, curr_offset_index)
            if table != None:
                table['prev_swing'] = curr_offset_index
                result.append(table)

        return result

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        raws = self.find_order_block(symbol, timeframe)
        for ob in raws:
            ob_idx = ob["index"]
            ob_color = ob["color"]
            ob_dir = ob["dir"]
            ob_low = ob["low"]
            ob_high = ob["high"]

            is_filled_order_block = False
            for i in range(ob_idx + 1, len(candles)):
                c = candles[i]
                # if ob_dir == TrendDir.UP and (c.get_trend_dir(self.trend_type) == TrendDir.UP or c.get_trend_dir(self.trend_type) == TrendDir.TOP):
                #     continue
                # if ob_dir == TrendDir.DOWN and (c.get_trend_dir(self.trend_type) == TrendDir.DOWN or c.get_trend_dir(self.trend_type) == TrendDir.BOTTOM):
                #     continue
                body_low = min(c.open, c.close) # c.low
                body_high = max(c.open, c.close) # c.high

                is_bullish = ob_dir == TrendDir.UP
                if (is_bullish and body_low < ob['high']) or (is_bullish == False and body_high > ob['low']):
                    # Order block is handled until — end it when the candle body breaks through
                    candles[ob_idx].set_indicator('order_block', {'low': ob_low, 'high': ob_high, 'color': ob_color, 'dir': ob_dir, 'until_idx': i})
                    is_filled_order_block = True

                if is_filled_order_block:
                    break

            if not is_filled_order_block:
                candles[ob_idx].set_indicator('order_block', {'low': ob_low, 'high': ob_high, 'color': ob_color, 'dir': ob_dir, 'until_idx': None})


class PDArrayIndicatorDrawer(IndicatorDrawer):
    def __init__(self, is_draw_fvg = True, is_draw_ob = True) -> None:
        super().__init__(name="fvg", color=None)

        self.is_draw_fvg = is_draw_fvg
        self.is_draw_ob = is_draw_ob

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        last_time = indexes[-1]

        for i in range(len(candles)):
            c = candles[i]
            if self.is_draw_ob and c.get_indicator('order_block') != None:
                start_num = i
                end_num = c.get_indicator('order_block')['until_idx'] or last_time

                width = end_num - start_num
                height = c.get_indicator('order_block')['high'] - c.get_indicator('order_block')['low']
                rect = Rectangle((start_num, c.get_indicator('order_block')['low']), width, height,
                                 facecolor=c.get_indicator('order_block')['color'], edgecolor=None, alpha=0.3)

                target_plot.add_patch(rect)
