from datetime import datetime
from typing import List

from matplotlib.axes import Axes

from indicator.trendline_const import TrendDir
from indicator.util import find_most_low, find_most_high
from model.candle import Candle
from indicator.indicator import Indicator
from indicator.indicator_drawer import IndicatorDrawer


class TrendLineIndicator(Indicator):
    def __init__(self, trend_type: str):
        super().__init__(name="trendline_" + trend_type)
        self.trend_type = trend_type

    def calculate(self, symbol, timeframe: str, end_time: datetime, candles, timestamps, opens, closes, lows, highs, volumes) -> None:
        # The trendline class does not consider main_trend_type. It is only used when computing pdarray.
        
        self.calculate_swing_lines(symbol, timeframe, end_time, candles)
        self.calculate_major_swing_lines(symbol, timeframe, end_time, candles)

    def calculate_swing_lines(self, symbol, timeframe, end_time: datetime, candles) -> None:
        # Defined in the subclass; major swing lines are handled based on this result.
        pass

    def calculate_major_swing_lines(self, symbol, timeframe, end_time: datetime, candles) -> None:
        next_swing_point = symbol.get_next_swing_point(timeframe, end_time, self.trend_type, 0)

        pivots = []
        trend_pivots = []

        if next_swing_point != None:
            curr_trend = TrendDir.NONE

            if next_swing_point.get_swing_dir(self.trend_type) == TrendDir.TOP:
                base_start_index = next_swing_point.index

                next_swing_low = symbol.get_next_swing_low(timeframe, end_time, self.trend_type, next_swing_point.index)
                if next_swing_low != None:
                    base_end_index = next_swing_low.index
                    check_index = base_end_index
                    curr_trend = TrendDir.DOWN

                    pivots.append((base_start_index, candles[base_start_index].high, TrendDir.TOP))
                    pivots.append((base_end_index, candles[base_end_index].low, TrendDir.BOTTOM))

            else:
                base_start_index = next_swing_point.index

                next_swing_high = symbol.get_next_swing_high(timeframe, end_time, self.trend_type, next_swing_point.index)
                if next_swing_high != None:
                    base_end_index = next_swing_high.index
                    check_index = base_end_index
                    curr_trend = TrendDir.UP

                    pivots.append((base_start_index, candles[base_start_index].low, TrendDir.BOTTOM))
                    pivots.append((base_end_index, candles[base_end_index].low, TrendDir.TOP))

            last_found_choch_index = -1
            while curr_trend != TrendDir.NONE:
                if curr_trend == TrendDir.UP:
                    next_low = symbol.get_next_swing_low(timeframe, end_time, self.trend_type, check_index)
                    next_high = symbol.get_next_swing_high(timeframe, end_time, self.trend_type, check_index)

                    if next_low == None:
                        trend_pivots.insert(0, (pivots[0][0], pivots[0][1], pivots[0][2]))
                        trend_pivots.append((pivots[len(pivots) - 1][0], pivots[len(pivots) - 1][1], pivots[len(pivots) - 1][2]))
                        break   # Reached the end, then break

                    if next_low != None and candles[base_start_index].low > next_low.low:
                        # Switch to downtrend
                        pivots.append((next_low.index, next_low.low, TrendDir.BOTTOM))

                        trend_pivots.append((base_end_index, candles[base_end_index].high, TrendDir.TOP))

                        # calculate choch
                        found_choch = False
                        prev_bottom = pivots[len(pivots) - 3][0]  # -1 is the newly added breakout swing point, -2 is the previous high, -3 is the previous low
                        for i in range(check_index, next_low.index + 1):
                            if candles[prev_bottom].low > candles[i].close:
                                candles[i].set_major_choch(self.trend_type, {'base_swing_point': prev_bottom, 'price': candles[prev_bottom].low, 'dir': TrendDir.DOWN})
                                candles[prev_bottom].set_major_choch_by(self.trend_type, {'by': i})
                                found_choch = True
                                break

                        if found_choch == False:
                            last_found_choch_index = prev_bottom    # Check during consecutive down swings.
                        else:
                            last_found_choch_index = -1

                        base_start_index = base_end_index
                        base_end_index = next_low.index
                        curr_trend = TrendDir.DOWN

                        check_index = next_low.index

                    elif next_high != None and candles[base_end_index].high < next_high.high:
                        # Switch to uptrend
                        most_low_index = find_most_low(candles, base_end_index + 1, next_high.index - 1)

                        pivots.append((most_low_index, candles[most_low_index].low, TrendDir.BOTTOM))
                        pivots.append((next_high.index, next_high.high, TrendDir.TOP))

                        # calculate bos
                        for i in range(next_low.index, next_high.index + 1):
                            if candles[base_end_index].high < candles[i].high:
                                candles[i].set_major_bos(self.trend_type, {'base_swing_point': base_end_index, 'price': candles[base_end_index].high, 'dir': TrendDir.UP})
                                break

                        # calculate choch (If no CHoCH detected when turning to uptrend)
                        if last_found_choch_index != -1:
                            found_choch = False
                            for i in range(base_end_index, next_high.index + 1):
                                if candles[last_found_choch_index].high < candles[i].close:
                                    candles[i].set_major_choch(self.trend_type, {'base_swing_point': last_found_choch_index, 'price': candles[last_found_choch_index].high, 'dir': TrendDir.UP})
                                    candles[last_found_choch_index].set_major_choch_by(self.trend_type, {'by': i})
                                    found_choch = True
                                    break

                            if found_choch == True:
                                last_found_choch_index = -1

                        base_start_index = next_low.index
                        base_end_index = next_high.index

                        check_index = base_end_index

                    else:
                        if next_high == None:
                            trend_pivots.insert(0, (pivots[0][0], pivots[0][1], pivots[0][2]))
                            trend_pivots.append((pivots[len(pivots) - 1][0], pivots[len(pivots) - 1][1], pivots[len(pivots) - 1][2]))
                            break
                        else:
                            check_index = next_high.index # ENGULFED

                elif curr_trend == TrendDir.DOWN:
                    next_high = symbol.get_next_swing_high(timeframe, end_time, self.trend_type, check_index)
                    next_low = symbol.get_next_swing_low(timeframe, end_time, self.trend_type, check_index)

                    if next_high == None:
                        trend_pivots.insert(0, (pivots[0][0], pivots[0][1], pivots[0][2]))
                        trend_pivots.append((pivots[len(pivots)-1][0], pivots[len(pivots)-1][1], pivots[len(pivots)-1][2]))
                        break   # Reached the end, then break

                    if next_high != None and candles[base_start_index].high < next_high.high:
                        # Switch to uptrend
                        pivots.append((next_high.index, next_high.high, TrendDir.TOP))

                        trend_pivots.append((base_end_index, candles[base_end_index].low, TrendDir.BOTTOM))

                        # calculate choch
                        found_choch = False
                        prev_top = pivots[len(pivots) - 3][0]  # -1 is the newly added breakout swing point, -2 is the previous high, -3 is the previous low
                        for i in range(check_index, next_high.index + 1):
                            if candles[prev_top].high < candles[i].close:
                                candles[i].set_major_choch(self.trend_type, {'base_swing_point': prev_top, 'price': candles[prev_top].high, 'dir': TrendDir.UP})
                                candles[prev_top].set_major_choch_by(self.trend_type, {'by': i})
                                found_choch = True
                                break

                        if found_choch == False:
                            last_found_choch_index = prev_top   # Check during consecutive up swings.
                        else:
                            last_found_choch_index = -1

                        base_start_index = base_end_index
                        base_end_index = next_high.index
                        curr_trend = TrendDir.UP

                        check_index = base_end_index

                    elif next_low != None and candles[base_end_index].low > next_low.low:
                        # Maintain downtrend
                        most_high_index = find_most_high(candles, base_end_index + 1, next_low.index - 1)

                        pivots.append((most_high_index, candles[most_high_index].high, TrendDir.TOP))
                        pivots.append((next_low.index, next_low.low, TrendDir.BOTTOM))

                        # calculate bos
                        for i in range(next_high.index, next_low.index + 1):
                            if candles[base_end_index].low > candles[i].low:
                                candles[i].set_major_bos(self.trend_type, {'base_swing_point': base_end_index, 'price': candles[base_end_index].low, 'dir': TrendDir.DOWN})
                                break

                        # calculate choch (When switching to downtrend, if no CHoCH is detected)
                        if last_found_choch_index != -1:
                            found_choch = False
                            for i in range(check_index, next_low.index + 1):
                                if candles[last_found_choch_index].low > candles[i].close:
                                    candles[i].set_major_choch(self.trend_type, {'base_swing_point': last_found_choch_index, 'price': candles[last_found_choch_index].low, 'dir': TrendDir.DOWN})
                                    candles[last_found_choch_index].set_major_choch_by(self.trend_type, {'by': i})
                                    found_choch = True
                                    break

                            if found_choch == True:
                                last_found_choch_index = -1

                        base_start_index = next_high.index
                        base_end_index = next_low.index

                        check_index = base_end_index

                    else:
                        if next_low == None:
                            trend_pivots.insert(0, (pivots[0][0], pivots[0][1], pivots[0][2]))
                            trend_pivots.append((pivots[len(pivots) - 1][0], pivots[len(pivots) - 1][1], pivots[len(pivots) - 1][2]))
                            break
                        else:
                            check_index = next_low.index # ENGULFED

            ## Apply candle directions between TOP and BOTTOM
            last_offset = 0
            for idx, price, t_dir in pivots:
                for i in range(last_offset, idx):
                    candles[i].set_major_swing_dir(self.trend_type, TrendDir.UP if t_dir == TrendDir.TOP else TrendDir.DOWN)
                last_offset = idx + 1

                candles[idx].set_major_swing_dir(self.trend_type, t_dir)
                candles[idx].set_major_swing_price(self.trend_type, price)

            last_offset = 0
            for idx, price, t_dir in trend_pivots:
                for i in range(last_offset, idx):
                    candles[i].set_trend_dir(self.trend_type, TrendDir.UP if t_dir == TrendDir.TOP else TrendDir.DOWN)
                last_offset = idx + 1

                candles[idx].set_trend_dir(self.trend_type, t_dir)
                candles[idx].set_trend_price(self.trend_type, price)

class TrendLineIndicatorDrawer(IndicatorDrawer):
    def __init__(self, trend_type: str, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('trendline_' + trend_type, trend_color)
        self.trend_type = trend_type
        self.swing_color = swing_color
        self.major_swing_color = major_swing_color

    # bos, choch
    def draw_swing(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        if self.swing_color != None:
            swing_prices = [c.get_swing_price(self.trend_type) for c in candles]
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
            major_swing_prices = [c.get_major_swing_price(self.trend_type) for c in candles]
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
            trend_prices = [c.get_trend_price(self.trend_type) for c in candles]
            trend_points = []
            for i in range(0, len(candles)):
                if trend_prices[i]:
                    trend_points.append((indexes[i], trend_prices[i]))

            if trend_points:
                trend_times, trend_vals = zip(*trend_points)
                target_plot.plot(trend_times, trend_vals, color=self.color, linestyle='--',
                                 label='Trend Line ' + self.trend_type)

    def draw_major_boses(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        bos_infos = [c.get_major_bos(self.trend_type) for c in candles]
        for i in range(len(bos_infos)):
            if bos_infos[i] == None:
                continue

            base_idx = bos_infos[i]['base_swing_point']
            price = bos_infos[i]['price']
            direction = bos_infos[i]['dir']

            # The price of the base candle (choose low/high depending on direction)
            if direction == TrendDir.DOWN:
                base_price = candles[base_idx].low
            else:
                base_price = candles[base_idx].high

            x_vals = [i, base_idx]
            y_vals = [price, base_price]

            target_plot.plot(x_vals, y_vals, color='black', linestyle='--', linewidth=1)

    def draw_major_choches(self, target_plot: Axes, indexes: List[int], candles: List[Candle]):
        bos_infos = [c.get_major_choch(self.trend_type) for c in candles]
        for i in range(len(bos_infos)):
            if bos_infos[i] == None:
                continue

            base_idx = bos_infos[i]['base_swing_point']
            price = bos_infos[i]['price']
            direction = bos_infos[i]['dir']

            # The price of the base candle (choose low/high depending on direction)
            if direction == TrendDir.DOWN:
                base_price = candles[base_idx].low
            else:
                base_price = candles[base_idx].high

            x_vals = [i, base_idx]
            y_vals = [price, base_price]

            target_plot.plot(x_vals, y_vals, color='black', linewidth=1.5)

    def draw(self, symbol, timeframe: str, end_time: datetime, target_plot: Axes, indexes: List[int], candles, timestamps, opens, closes, lows, highs, volumes):
        self.draw_swing(target_plot, indexes, candles)
        self.draw_major_swing(target_plot, indexes, candles)
        self.draw_trend(target_plot, indexes, candles)

        # major boses
        self.draw_major_boses(target_plot, indexes, candles)
        # major choches
        self.draw_major_choches(target_plot, indexes, candles)


