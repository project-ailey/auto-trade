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

    def __init__(self, trend_type: str, trend_atr_multiplier: float):
        super().__init__(name="trendline_" + trend_type)
        self.trend_type = trend_type
        self.trendline_atr_multiplier = trend_atr_multiplier

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

    @staticmethod
    def apply_zigzag_with_atr(swing_dir_key_name, swing_price_key_name, atr_multiplier, candles: List[Candle]) -> None:
        # Step 1: Find the index of the first candle with a valid ATR
        start_index = -1
        for i, candle in enumerate(candles):
            if candle.get_indicator('atr') is not None:
                start_index = i
                break

        # If there is no valid starting point or insufficient data, exit the function
        if start_index == -1 or len(candles) < start_index + 2:
            print("lack atrs")
            return

        # Step 2: Initialize variables starting from the valid point
        pivots = []
        last_pivot_price = candles[start_index].close
        trend_dir = None

        candidate_pivot_price = last_pivot_price
        candidate_pivot_idx = start_index

        # Step 3: Main loop starting from the next candle after the valid point
        for i in range(start_index + 1, len(candles)):
            current_candle = candles[i]
            atr_at_pivot = candles[candidate_pivot_idx].get_indicator('atr')

            # Assume there are no candles without ATR after start_index
            # But if being defensive, a check could be added
            if atr_at_pivot is None: continue

            threshold = atr_multiplier * atr_at_pivot

            if trend_dir is None:  # Determine initial trend
                if current_candle.high - last_pivot_price >= threshold:
                    trend_dir = TrendLineIndicator.UP
                    candidate_pivot_price = current_candle.high
                    candidate_pivot_idx = i
                elif last_pivot_price - current_candle.low >= threshold:
                    trend_dir = TrendLineIndicator.DOWN
                    candidate_pivot_price = current_candle.low
                    candidate_pivot_idx = i

            elif trend_dir == TrendLineIndicator.UP:  # Uptrend (finding highs)
                if current_candle.high > candidate_pivot_price:
                    candidate_pivot_price = current_candle.high
                    candidate_pivot_idx = i
                else:
                    retrace_price = candidate_pivot_price - current_candle.low
                    if retrace_price >= threshold:
                        pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendLineIndicator.TOP))
                        trend_dir = TrendLineIndicator.DOWN
                        candidate_pivot_price = current_candle.low
                        candidate_pivot_idx = i

            elif trend_dir == TrendLineIndicator.DOWN:  # Downtrend (finding lows)
                if current_candle.low < candidate_pivot_price:
                    candidate_pivot_price = current_candle.low
                    candidate_pivot_idx = i
                else:
                    retrace_price = current_candle.high - candidate_pivot_price
                    if retrace_price >= threshold:
                        pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendLineIndicator.BOTTOM))
                        trend_dir = TrendLineIndicator.UP
                        candidate_pivot_price = current_candle.high
                        candidate_pivot_idx = i

        # Apply confirmed pivots to candles
        last_offset = 0
        for idx, price, t_dir in pivots:
            for i in range(last_offset, idx):
                candles[idx].set_indicator(swing_dir_key_name, TrendLineIndicator.UP if t_dir == TrendLineIndicator.TOP else TrendLineIndicator.DOWN)
            last_offset = idx + 1

            candles[idx].set_indicator(swing_price_key_name, price)
            candles[idx].set_indicator(swing_dir_key_name, t_dir)

    def calculate(self, symbol, timeframe: str, timestamps, opens, closes, lows, highs, volumes) -> None:
        candles = symbol.get_candles(timeframe)

        if len(candles) == 0:
            return

        self.calculate_swing_lines(candles)
        self.calculate_trends_dirs(candles)

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        pass

    def calculate_trends_dirs(self, candles: List[Candle]) -> None:
        TrendLineIndicator.apply_zigzag_with_atr('trend_dir_' + self.trend_type, 'trend_price_' + self.trend_type, self.trendline_atr_multiplier, candles)

class TrendLineIndicatorDrawer(IndicatorDrawer):
    def __init__(self, trend_type: str, swing_color: str, trend_color: str):
        super().__init__('trendline_' + trend_type, trend_color)
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
