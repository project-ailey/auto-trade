from typing import List
from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineZigZagAtrIndicator(TrendLineIndicator):
    def __init__(self, zigzag_atr_multiplier: float = 1.1, trend_atr_multiplier: float = 2):
        super().__init__(trend_type="zigzag_atr", trend_atr_multiplier=trend_atr_multiplier)

        self.zigzag_atr_multiplier = zigzag_atr_multiplier

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
                candles[i].set_indicator(swing_dir_key_name,
                                           TrendLineIndicator.UP if t_dir == TrendLineIndicator.TOP else TrendLineIndicator.DOWN)
            last_offset = idx + 1

            candles[idx].set_indicator(swing_price_key_name, price)
            candles[idx].set_indicator(swing_dir_key_name, t_dir)

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        TrendLineZigZagAtrIndicator.apply_zigzag_with_atr('swing_dir_' + self.trend_type, 'swing_price_' + self.trend_type, self.zigzag_atr_multiplier, candles)

class TrendLineZigZagAtrIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('zigzag_atr', swing_color, major_swing_color, trend_color)