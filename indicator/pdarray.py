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

    def find_order_block(self, symbol, timeframe: str, offset_index: int, override_swing_dir: int = TrendDir.NONE, can_find_if_not_found: bool = False, find_dir: int = 0):
        candles = symbol.get_candles(timeframe)

        swing_dir = candles[offset_index].get_major_swing_dir(self.trend_type) if override_swing_dir == TrendDir.NONE else override_swing_dir   # for recursive
        price_dir = TrendDir.DOWN if swing_dir == TrendDir.TOP else TrendDir.UP
        ob_color = '#7A261F' if swing_dir == TrendDir.TOP else '#003F3F'

        if swing_dir == TrendDir.TOP:
            pass
        elif swing_dir == TrendDir.BOTTOM:
            pass
        else:
            return None

        upper_shadow_high = candles[offset_index].high
        upper_shadow_low = max(candles[offset_index].open, candles[offset_index].close)
        upper_shadow_size = upper_shadow_high - upper_shadow_low

        lower_shadow_high = min(candles[offset_index].open, candles[offset_index].close)
        lower_shadow_low = candles[offset_index].low
        lower_shadow_size = lower_shadow_high - lower_shadow_low

        if candles[offset_index].has_long_shadow(swing_dir == TrendDir.TOP, 1):
            # Rejection Block – When a long upper wick appears at the start of a down move
            if swing_dir == TrendDir.TOP:
                high = upper_shadow_high
                low = upper_shadow_low
            else:
                high = lower_shadow_high
                low = lower_shadow_low

            return {"type": "rejection", "high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

        elif swing_dir == TrendDir.BOTTOM and candles[offset_index].has_long_upper_shadow(1):
            # Inverted hammer at the low point (a case where the short-selling force was blocked by major players)
            high = candles[offset_index].high
            low = max(candles[offset_index].open, candles[offset_index].close)
            return {"type": "order", "high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

        elif candles[offset_index].get_indicator('atr') and (upper_shadow_size if swing_dir == TrendDir.TOP else lower_shadow_size) > candles[offset_index].get_indicator('atr'):
            # Star shape but with a long wick
            if swing_dir == TrendDir.TOP:
                high = upper_shadow_high
                low = upper_shadow_low
            else:
                high = lower_shadow_high
                low = lower_shadow_low

            return {"type": "rejection", "high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

        elif candles[offset_index].is_bullish() if swing_dir == TrendDir.TOP else candles[offset_index].is_bearish():
            # Order Block – When there is an order block at the swing point
            low = candles[offset_index].low
            high = candles[offset_index].high

            return {"type": "order", "high": high, "low": low, "color": ob_color, "index": offset_index, "dir": price_dir}

        else:
            # If there is no order block at the swing point, look before and after
            if can_find_if_not_found:
                if find_dir == 0:
                    post_dir_ob = self.find_order_block(symbol, timeframe, offset_index + 1, swing_dir, can_find_if_not_found, 1) # post has higher priority
                    prev_dir_ob = self.find_order_block(symbol, timeframe, offset_index - 1, swing_dir, can_find_if_not_found, -1)  # If there's no post, check prev

                    if post_dir_ob != None and prev_dir_ob == None:
                        return post_dir_ob
                    elif post_dir_ob == None and prev_dir_ob != None:
                        return prev_dir_ob
                    else:
                        if swing_dir == TrendDir.TOP:
                            if post_dir_ob['high'] > prev_dir_ob['high']:
                                return post_dir_ob
                            else:
                                return prev_dir_ob
                        elif swing_dir == TrendDir.BOTTOM:
                            if post_dir_ob['low'] < prev_dir_ob['low']:
                                return post_dir_ob
                            else:
                                return prev_dir_ob
                        else:
                            return None

                elif find_dir == 1:
                    return self.find_order_block(symbol, timeframe, offset_index + 1, swing_dir, can_find_if_not_found, 1)

                elif find_dir == -1:
                    return self.find_order_block(symbol, timeframe, offset_index - 1, swing_dir, can_find_if_not_found, -1)
            else:
                return None

    def find_fvg_blocks(self, symbol, timeframe: str, base_swing_index: int):
        candles = symbol.get_candles(timeframe)

        base_swing_dir = candles[base_swing_index].get_major_swing_dir(self.trend_type)

        result = []
        for i in range(base_swing_index + 2, len(candles)):
            center_idx = i - 1
            prev, center, post = candles[i - 2], candles[center_idx], candles[i]

            if prev.index != base_swing_index and candles[prev.index].has_major_swing_point(self.trend_type):
                break

            if base_swing_dir == TrendDir.BOTTOM and post.low > prev.high and center.is_bullish():    # Uptrend
                result.append({"type": "fvg", "high": post.low, "low": prev.high, "color": 'teal', "index": center_idx, "dir": TrendDir.UP})

            elif base_swing_dir == TrendDir.TOP and post.high < prev.low and center.is_bearish():  # Downtrend
                result.append({"type": "fvg", "high": prev.low, "low": post.high, "color": 'tomato', "index": center_idx, "dir": TrendDir.DOWN})

        return result


    def find_pdarray_blocks(self, symbol, timeframe: str):
        base_swing_index = 0

        result = []
        while True:
            next_swing_point = symbol.get_next_major_swing_point(timeframe, self.trend_type, base_swing_index)
            if next_swing_point == None:
                break

            base_swing_index = next_swing_point.index

            order_block = self.find_order_block(symbol, timeframe, base_swing_index, TrendDir.NONE, True, 0)
            if order_block != None:
                if base_swing_index == order_block["index"]:
                    high = order_block["high"]
                    low = order_block["low"]
                    swing_dir = TrendDir.TOP if order_block["dir"] == TrendDir.DOWN else TrendDir.BOTTOM

                    next_ob = self.find_order_block(symbol, timeframe, base_swing_index + 1, swing_dir, False, 0)
                    if next_ob != None and high > next_ob['high'] and low < next_ob['low']: # If the next order block is contained within the structure, replace it with that
                        order_block = next_ob


                # Find the fair value gap
                fvgs = self.find_fvg_blocks(symbol, timeframe, base_swing_index)
                if len(fvgs) > 0:   # Add an order block only if at least one FVG exists
                    order_block["base_swing_index"] = base_swing_index
                    result.append(order_block)

                    for f in fvgs:
                        f["base_swing_index"] = base_swing_index
                        result.append(f)

        return result

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        raws = self.find_pdarray_blocks(symbol, timeframe)
        for ob in raws:
            ob_type = ob["type"]
            ob_idx = ob["index"]
            ob_color = ob["color"]
            ob_dir = ob["dir"]
            ob_low = ob["low"]
            ob_high = ob["high"]
            ob_base_swing_idx = ob["base_swing_index"]

            is_filled_order_block = False
            for i in range(ob_idx + 1, len(candles)):
                c = candles[i]

                if i <= ob_base_swing_idx:    # If the candle before the inflection point is defined as an order block, check the direction after the inflection point
                    continue
                if ob_dir == TrendDir.UP and (c.get_major_swing_dir(self.trend_type) == TrendDir.UP or c.get_major_swing_dir(self.trend_type) == TrendDir.TOP):
                    continue
                if ob_dir == TrendDir.DOWN and (c.get_major_swing_dir(self.trend_type) == TrendDir.DOWN or c.get_major_swing_dir(self.trend_type) == TrendDir.BOTTOM):
                    continue
                body_low = min(c.open, c.close) # c.low
                body_high = max(c.open, c.close) # c.high

                is_bullish = ob_dir == TrendDir.UP
                if (is_bullish and body_low < ob['high']) or (is_bullish == False and body_high > ob['low']):
                    # Order block is handled until — end it when the candle body breaks through
                    candles[ob_idx].set_indicator('pdarray', {'type': ob_type, 'low': ob_low, 'high': ob_high, 'color': ob_color, 'dir': ob_dir, 'until_idx': i})
                    is_filled_order_block = True

                if is_filled_order_block:
                    break

            if not is_filled_order_block:
                candles[ob_idx].set_indicator('pdarray', {'type': ob_type, 'low': ob_low, 'high': ob_high, 'color': ob_color, 'dir': ob_dir, 'until_idx': None})


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
            if c.get_indicator('pdarray') != None:
                type = c.get_indicator('pdarray')['type']
                if type == 'fvg' and self.is_draw_fvg == False:
                    continue
                if (type == 'order' or type == 'rejection') and self.is_draw_ob == False:
                    continue

                start_num = i
                end_num = c.get_indicator('pdarray')['until_idx'] or last_time

                width = end_num - start_num
                height = c.get_indicator('pdarray')['high'] - c.get_indicator('pdarray')['low']
                rect = Rectangle((start_num, c.get_indicator('pdarray')['low']), width, height,
                                 facecolor=c.get_indicator('pdarray')['color'], edgecolor=None, alpha=0.3)

                target_plot.add_patch(rect)
