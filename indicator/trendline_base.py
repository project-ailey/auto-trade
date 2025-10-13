from typing import List

from matplotlib.axes import Axes

from model.candle import Candle
from indicator.indicator import Indicator
from indicator.indicator_drawer import IndicatorDrawer


class TrendLineIndicator(Indicator):
    NONE = 0
    UP = 1
    DOWN = 2
    TOP = 3
    BOTTOM = 4
    ENGULFED_IN_UP = 5,
    ENGULFED_IN_DOWN = 6,

    def __init__(self, trend_type: str):
        super().__init__(name="trendline_" + trend_type)
        self.trend_type = trend_type

    @staticmethod
    def get_prev_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return 0 if current_index > 0 and len(candles) > 0 else None

    @staticmethod
    def get_prev_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return 0 if current_index > 0 and len(candles) > 0 else None

    @staticmethod
    def get_next_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return None

    @staticmethod
    def get_next_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return None

    @staticmethod
    def get_prev_swing_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return None

    @staticmethod
    def get_next_swing_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return None

    @staticmethod
    def get_prev_trend_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return 0 if current_index > 0 and len(candles) > 0 else None

    @staticmethod
    def get_prev_trend_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return 0 if current_index > 0 and len(candles) > 0 else None

    @staticmethod
    def get_prev_trend_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return None

    @staticmethod
    def get_next_trend_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('trend_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return None



    def calculate(self, symbol, timeframe: str) -> None:
        candles = symbol.get_candles(timeframe)

        if len(candles) == 0:
            return

        self.calculate_swing_lines(candles)
        self.calculate_trends_dirs(candles)

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        pass

    def calculate_trends_dirs(self, candles: List[Candle]) -> None:
        curr_index = 0

        trend_dir_indicator_name = "trend_dir_" + self.trend_type
        trend_price_indicator_name = "trend_price_" + self.trend_type

        swing_dir_indicator_name = "swing_dir_" + self.trend_type
        swing_price_indicator_name = "swing_price_" + self.trend_type

        # Based on the first candle, determine the direction unconditionally. Doji is treated as bearish.
        is_grab = False
        for i in range(len(candles)):
            if candles[i].get_indicator('swing_dir_' + self.trend_type) != None:
                candles[i].set_indicator(trend_dir_indicator_name, candles[i].get_indicator('swing_dir_' + self.trend_type))
                candles[i].set_indicator(trend_price_indicator_name, candles[i].get_indicator('swing_price_' + self.trend_type))
                is_grab = True
                break

        if is_grab == False:
            return

        while curr_index < len(candles):
            next_high = TrendLineIndicator.get_next_swing_high(self.trend_type, curr_index, candles)
            next_low = TrendLineIndicator.get_next_swing_low(self.trend_type, curr_index, candles)
            prev_high = TrendLineIndicator.get_prev_swing_high(self.trend_type, curr_index, candles)
            prev_low = TrendLineIndicator.get_prev_swing_low(self.trend_type, curr_index, candles)

            if candles[curr_index].get_indicator(trend_dir_indicator_name) == TrendLineIndicator.UP or candles[curr_index].get_indicator(trend_dir_indicator_name) == TrendLineIndicator.TOP:
                if next_high and candles[next_high].high >= candles[curr_index].high:  # continue uptrend
                    for i in range(curr_index, next_high + 1):
                        candles[i].set_indicator(trend_dir_indicator_name, TrendLineIndicator.UP)
                    curr_index = next_high

                elif prev_low != None and next_low and candles[prev_low].low > candles[next_low].low:  # switch to downtrend
                    candles[curr_index].set_indicator(trend_dir_indicator_name, TrendLineIndicator.TOP)
                    candles[curr_index].set_indicator(trend_price_indicator_name, candles[curr_index].high)  # only set price on switch
                    candles[next_low].set_indicator(trend_dir_indicator_name, TrendLineIndicator.DOWN)
                    curr_index = next_low

                else:  # neither uptrend nor downtrend
                    is_grab = False
                    for i in range(curr_index + 1, len(candles)):
                        next_swing_point = TrendLineIndicator.get_next_swing_swing_point(self.trend_type, i, candles)  # keep searching until up or down

                        if next_swing_point and candles[next_swing_point].high >= candles[curr_index].high:  # confirm uptrend, prioritize uptrend
                            for j in range(curr_index, next_swing_point + 1):
                                candles[j].set_indicator(trend_dir_indicator_name, TrendLineIndicator.UP)

                            curr_index = next_swing_point
                            is_grab = True
                            break

                        elif prev_low != None and next_swing_point and candles[next_swing_point].low < candles[prev_low].low:  # confirm downtrend
                            candles[curr_index].set_indicator(trend_dir_indicator_name, TrendLineIndicator.TOP)
                            candles[curr_index].set_indicator(trend_price_indicator_name, candles[curr_index].high)  # only set price on switch
                            for j in range(curr_index + 1, next_swing_point + 1):
                                candles[j].set_indicator(trend_dir_indicator_name, TrendLineIndicator.DOWN)

                            curr_index = next_swing_point
                            is_grab = True
                            break

                    if is_grab == False:
                        candles[len(candles) - 1].set_indicator(trend_price_indicator_name, candles[len(candles) - 1].high)  # connect to last candle
                        curr_index = len(candles)  # reached the end but no breakout from last structure

            elif candles[curr_index].get_indicator(trend_dir_indicator_name) == TrendLineIndicator.DOWN or candles[curr_index].get_indicator(trend_dir_indicator_name) == TrendLineIndicator.BOTTOM:
                if next_low and candles[next_low].low < candles[curr_index].low:  # continue downtrend
                    for i in range(curr_index, next_low + 1):
                        candles[i].set_indicator(trend_dir_indicator_name, TrendLineIndicator.DOWN)
                    curr_index = next_low

                elif prev_high and next_high and candles[prev_high].high <= candles[next_high].high:  # switch to uptrend
                    candles[curr_index].set_indicator(trend_dir_indicator_name, TrendLineIndicator.BOTTOM)
                    candles[curr_index].set_indicator(trend_price_indicator_name, candles[curr_index].low)  # only set price on switch
                    candles[next_high].set_indicator(trend_dir_indicator_name, TrendLineIndicator.UP)
                    curr_index = next_high

                else:  # neither uptrend nor downtrend
                    is_grab = False
                    for i in range(curr_index + 1, len(candles)):
                        next_swing_point = TrendLineIndicator.get_next_swing_swing_point(self.trend_type, i, candles)  # keep searching until up or down

                        if next_swing_point and candles[next_swing_point].low < candles[curr_index].low:  # confirm downtrend, prioritize downtrend
                            for j in range(curr_index, next_swing_point + 1):
                                candles[j].set_indicator(trend_dir_indicator_name, TrendLineIndicator.DOWN)

                            curr_index = next_swing_point
                            is_grab = True
                            break

                        elif prev_high and next_swing_point and candles[next_swing_point].high >= candles[prev_high].high:  # confirm uptrend
                            candles[curr_index].set_indicator(trend_dir_indicator_name, TrendLineIndicator.BOTTOM)
                            candles[curr_index].set_indicator(trend_price_indicator_name, candles[curr_index].low)  # only set price on switch
                            for j in range(curr_index + 1, next_swing_point + 1):
                                candles[j].set_indicator(trend_dir_indicator_name, TrendLineIndicator.UP)

                            curr_index = next_swing_point
                            is_grab = True
                            break

                    if is_grab == False:
                        candles[len(candles) - 1].set_indicator(trend_price_indicator_name, candles[len(candles) - 1].low)  # connect to last candle
                        curr_index = len(candles)  # reached the end but no breakout from last structure
            else:
                curr_index += 1

class TrendLineIndicatorDrawer(IndicatorDrawer):
    def __init__(self, trend_type: str, color: str, swing_color: str):
        super().__init__('trendline_' + trend_type, color)
        self.trend_type = trend_type
        self.swing_color = swing_color

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        if self.swing_color != None:
            swing_prices = [c.get_indicator("swing_price_" + self.trend_type) for c in candles]
            swing_points = []
            for i in range(0, len(candles)):
                if swing_prices[i]:
                    swing_points.append((indexes[i], swing_prices[i]))

            if swing_points:
                trend_times, trend_vals = zip(*swing_points)
                target_plot.plot(trend_times, trend_vals, color=self.swing_color, linestyle='--', label='Swing Line ' + self.trend_type)

        if self.color != None:
            trend_prices = [c.get_indicator("trend_price_" + self.trend_type) for c in candles]
            trend_points = []
            for i in range(0, len(candles)):
                if trend_prices[i]:
                    trend_points.append((indexes[i], trend_prices[i]))

            if trend_points:
                trend_times, trend_vals = zip(*trend_points)
                target_plot.plot(trend_times, trend_vals, color=self.color, linestyle='--', label='Trend Line ' + self.trend_type)
