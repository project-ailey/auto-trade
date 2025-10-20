from typing import List

from matplotlib.axes import Axes

from indicator.util import find_most_low, find_most_high
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

    def __init__(self, trend_type: str, trend_atr_multiplier: float):
        super().__init__(name="trendline_" + trend_type)
        self.trend_type = trend_type
        self.trendline_atr_multiplier = trend_atr_multiplier

    # swing
    @staticmethod
    def get_prev_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return -1

    @staticmethod
    def get_prev_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_next_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return -1

    @staticmethod
    def get_next_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_prev_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_next_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    # major swing
    @staticmethod
    def get_prev_major_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return -1

    @staticmethod
    def get_prev_major_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_next_major_swing_high(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.TOP):
                return i
        return -1

    @staticmethod
    def get_next_major_swing_low(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_prev_major_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index - 1, -1, -1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    @staticmethod
    def get_next_major_swing_point(trend_type, current_index, candles: List[Candle]):
        for i in range(current_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.TOP) or (
                    c.get_indicator('major_swing_dir_' + trend_type) == TrendLineIndicator.BOTTOM):
                return i
        return -1

    # swing
    def set_swing_dir(self, candle, value):
        candle.set_indicator("swing_dir_" + self.trend_type, value)

    def get_swing_dir(self, candle):
        return candle.get_indicator("swing_dir_" + self.trend_type)

    def set_swing_price(self, candle, value):
        candle.set_indicator("swing_price_" + self.trend_type, value)

    def get_swing_price(self, candle):
        return candle.get_indicator("swing_price_" + self.trend_type)

    # major swing
    def set_major_swing_dir(self, candle, value):
        candle.set_indicator("major_swing_dir_" + self.trend_type, value)

    def get_major_swing_dir(self, candle):
        return candle.get_indicator("major_swing_dir_" + self.trend_type)

    def set_major_swing_price(self, candle, value):
        candle.set_indicator("major_swing_price_" + self.trend_type, value)

    def get_major_swing_price(self, candle):
        return candle.get_indicator("major_swing_price_" + self.trend_type)

    # trend
    def set_trend_dir(self, candle, value):
        candle.set_indicator("trend_dir_" + self.trend_type, value)

    def get_trend_dir(self, candle):
        return candle.get_indicator("trend_dir_" + self.trend_type)

    def set_trend_price(self, candle, value):
        candle.set_indicator("trend_price_" + self.trend_type, value)

    def get_trend_price(self, candle):
        return candle.get_indicator("trend_price_" + self.trend_type)

    # bos, choch
    def set_major_bos(self, candle, value):
        candle.set_indicator("major_bos_" + self.trend_type, value)

    def get_major_bos(self, candle):
        return candle.get_indicator("major_bos_" + self.trend_type)

    def set_major_choch(self, candle, value):
        candle.set_indicator("major_choch_" + self.trend_type, value)

    def get_major_choch(self, candle):
        return candle.get_indicator("major_choch_" + self.trend_type)

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        if len(candles) == 0:
            return

        self.calculate_swing_lines(candles)
        self.calculate_major_swing_lines(candles)

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        pass

    def calculate_major_swing_lines(self, candles: List[Candle]) -> None:
        next_index = TrendLineIndicator.get_next_swing_point(self.trend_type, 0, candles)

        pivots = []
        trend_pivots = []

        if next_index != -1:
            if self.get_swing_dir(candles[next_index]) == TrendLineIndicator.TOP:
                base_start_index = next_index
                base_end_index = TrendLineIndicator.get_next_swing_low(self.trend_type, next_index, candles)
                check_index = base_end_index
                curr_trend = TrendLineIndicator.DOWN

                pivots.append((base_start_index, candles[base_start_index].high, TrendLineIndicator.TOP))
                pivots.append((base_end_index, candles[base_end_index].low, TrendLineIndicator.BOTTOM))

            else:
                base_start_index = next_index
                base_end_index = TrendLineIndicator.get_next_swing_high(self.trend_type, next_index, candles)
                check_index = base_end_index
                curr_trend = TrendLineIndicator.UP

                pivots.append((base_start_index, candles[base_start_index].low, TrendLineIndicator.BOTTOM))
                pivots.append((base_end_index, candles[base_end_index].low, TrendLineIndicator.TOP))

            while True:
                if curr_trend == TrendLineIndicator.UP:
                    next_low = TrendLineIndicator.get_next_swing_low(self.trend_type, check_index, candles)
                    next_high = TrendLineIndicator.get_next_swing_high(self.trend_type, check_index, candles)

                    if next_low == -1:
                        break   # Reached the end, then break

                    if next_low != -1 and candles[base_start_index].low > candles[next_low].low:
                        # Switch to downtrend
                        pivots.append((next_low, candles[next_low].low, TrendLineIndicator.BOTTOM))

                        trend_pivots.append((base_end_index, candles[base_end_index].high, TrendLineIndicator.TOP))

                        # calculate choch
                        for i in range(check_index, next_low + 1):
                            prev_bottom = pivots[len(pivots) - 3][0]    # -1 is the newly added breakout swing point, -2 is the previous high, -3 is the previous low
                            if candles[prev_bottom].low > candles[i].close:
                                self.set_major_choch(candles[i], {'base_swing_point': prev_bottom, 'price': candles[prev_bottom].low, 'dir': TrendLineIndicator.DOWN})
                                break

                        base_start_index = base_end_index
                        base_end_index = next_low
                        curr_trend = TrendLineIndicator.DOWN

                        check_index = next_low

                    elif next_high != -1 and candles[base_end_index].high < candles[next_high].high:
                        # Switch to uptrend
                        most_low_index = find_most_low(candles, base_end_index + 1, next_high - 1)

                        pivots.append((most_low_index, candles[most_low_index].low, TrendLineIndicator.BOTTOM))
                        pivots.append((next_high, candles[next_high].high, TrendLineIndicator.TOP))

                        # calculate bos
                        for i in range(next_low, next_high + 1):
                            if candles[base_end_index].high < candles[i].high:
                                self.set_major_bos(candles[i], {'base_swing_point': base_end_index, 'price': candles[base_end_index].high, 'dir': TrendLineIndicator.UP})
                                break

                        base_start_index = next_low
                        base_end_index = next_high

                        check_index = base_end_index

                    else:
                        if next_high == -1:
                            break
                        else:
                            check_index = next_high # ENGULFED

                elif curr_trend == TrendLineIndicator.DOWN:
                    next_high = TrendLineIndicator.get_next_swing_high(self.trend_type, check_index, candles)
                    next_low = TrendLineIndicator.get_next_swing_low(self.trend_type, check_index, candles)

                    if next_high == -1:
                        break   # Reached the end, then break

                    if next_high != -1 and candles[base_start_index].high < candles[next_high].high:
                        # Switch to uptrend
                        pivots.append((next_high, candles[next_high].high, TrendLineIndicator.TOP))

                        trend_pivots.append((base_end_index, candles[base_end_index].low, TrendLineIndicator.BOTTOM))

                        # calculate choch
                        for i in range(check_index, next_high + 1):
                            prev_top = pivots[len(pivots) - 3][0]   # -1 is the newly added breakout swing point, -2 is the previous high, -3 is the previous low
                            if candles[prev_top].high < candles[i].close:
                                self.set_major_choch(candles[i], {'base_swing_point': prev_top, 'price': candles[prev_top].high, 'dir': TrendLineIndicator.UP})
                                break

                        base_start_index = base_end_index
                        base_end_index = next_high
                        curr_trend = TrendLineIndicator.UP

                        check_index = base_end_index

                    elif next_low != -1 and candles[base_end_index].low > candles[next_low].low:
                        # Maintain downtrend
                        most_high_index = find_most_high(candles, base_end_index + 1, next_low - 1)

                        pivots.append((most_high_index, candles[most_high_index].high, TrendLineIndicator.TOP))
                        pivots.append((next_low, candles[next_low].low, TrendLineIndicator.BOTTOM))

                        # calculate bos
                        for i in range(next_high, next_low + 1):
                            if candles[base_end_index].low > candles[i].low:
                                self.set_major_bos(candles[i], {'base_swing_point': base_end_index, 'price': candles[base_end_index].low, 'dir': TrendLineIndicator.DOWN})
                                break

                        base_start_index = next_high
                        base_end_index = next_low

                        check_index = base_end_index

                    else:
                        if next_low == -1:
                            break
                        else:
                            check_index = next_low # ENGULFED

            ## Apply candle directions between TOP and BOTTOM
            last_offset = 0
            for idx, price, t_dir in pivots:
                for i in range(last_offset, idx):
                    self.set_major_swing_dir(candles[i], TrendLineIndicator.UP if t_dir == TrendLineIndicator.TOP else TrendLineIndicator.DOWN)
                last_offset = idx + 1

                self.set_major_swing_dir(candles[idx], t_dir)
                self.set_major_swing_price(candles[idx], price)

            last_offset = 0
            for idx, price, t_dir in trend_pivots:
                for i in range(last_offset, idx):
                    self.set_trend_dir(candles[i], TrendLineIndicator.UP if t_dir == TrendLineIndicator.TOP else TrendLineIndicator.DOWN)
                last_offset = idx + 1

                self.set_trend_dir(candles[idx], t_dir)
                self.set_trend_price(candles[idx], price)

class TrendLineIndicatorDrawer(IndicatorDrawer):
    def __init__(self, trend_type: str, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('trendline_' + trend_type, trend_color)
        self.trend_type = trend_type
        self.swing_color = swing_color
        self.major_swing_color = major_swing_color

    def get_swing_price(self, candle):
        return candle.get_indicator("swing_price_" + self.trend_type)

    def get_major_swing_price(self, candle):
        return candle.get_indicator("major_swing_price_" + self.trend_type)

    def get_trend_price(self, candle):
        return candle.get_indicator("trend_price_" + self.trend_type)

    # bos, choch
    def get_major_bos(self, candle):
        return candle.get_indicator("major_bos_" + self.trend_type)

    def get_major_choch(self, candle):
        return candle.get_indicator("major_choch_" + self.trend_type)

    def draw_swing(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        if self.swing_color != None:
            swing_prices = [self.get_swing_price(c) for c in candles]
            swing_points = []
            for i in range(0, len(candles)):
                if swing_prices[i]:
                    swing_points.append((indexes[i], swing_prices[i]))

            if swing_points:
                trend_times, trend_vals = zip(*swing_points)
                target_plot.plot(trend_times, trend_vals, color=self.swing_color, linestyle='--',
                                 label='Swing Line ' + self.trend_type)

    def draw_major_swing(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        if self.major_swing_color != None:
            major_swing_prices = [self.get_major_swing_price(c) for c in candles]
            major_swing_points = []
            for i in range(0, len(candles)):
                if major_swing_prices[i]:
                    major_swing_points.append((indexes[i], major_swing_prices[i]))

            if major_swing_points:
                trend_times, trend_vals = zip(*major_swing_points)
                target_plot.plot(trend_times, trend_vals, color=self.major_swing_color, linestyle='--',
                                 label='Major Swing Line ' + self.trend_type)

    def draw_trend(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        if self.color != None:
            trend_prices = [self.get_trend_price(c) for c in candles]
            trend_points = []
            for i in range(0, len(candles)):
                if trend_prices[i]:
                    trend_points.append((indexes[i], trend_prices[i]))

            if trend_points:
                trend_times, trend_vals = zip(*trend_points)
                target_plot.plot(trend_times, trend_vals, color=self.color, linestyle='--',
                                 label='Trend Line ' + self.trend_type)

    def draw_major_boses(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        bos_infos = [self.get_major_bos(c) for c in candles]
        for i in range(len(bos_infos)):
            if bos_infos[i] == None:
                continue

            base_idx = bos_infos[i]['base_swing_point']
            price = bos_infos[i]['price']
            direction = bos_infos[i]['dir']

            # The price of the base candle (choose low/high depending on direction)
            if direction == TrendLineIndicator.DOWN:
                base_price = candles[base_idx].low
            else:
                base_price = candles[base_idx].high

            x_vals = [i, base_idx]
            y_vals = [price, base_price]

            target_plot.plot(x_vals, y_vals, color='black', linestyle='--', linewidth=1)

    def draw_major_choches(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        bos_infos = [self.get_major_choch(c) for c in candles]
        for i in range(len(bos_infos)):
            if bos_infos[i] == None:
                continue

            base_idx = bos_infos[i]['base_swing_point']
            price = bos_infos[i]['price']
            direction = bos_infos[i]['dir']

            # The price of the base candle (choose low/high depending on direction)
            if direction == TrendLineIndicator.DOWN:
                base_price = candles[base_idx].low
            else:
                base_price = candles[base_idx].high

            x_vals = [i, base_idx]
            y_vals = [price, base_price]

            target_plot.plot(x_vals, y_vals, color='black', linewidth=1.5)

    def draw(self, symbol, timeframe: str, target_plot: Axes, indexes: List[int], timestamps, opens, closes, lows, highs, volumes):
        candles = symbol.get_candles(timeframe)

        self.draw_swing(target_plot, indexes, candles)
        self.draw_major_swing(target_plot, indexes, candles)
        self.draw_trend(target_plot, indexes, candles)

        # major boses
        self.draw_major_boses(target_plot, indexes, candles)
        # major choches
        self.draw_major_choches(target_plot, indexes, candles)


