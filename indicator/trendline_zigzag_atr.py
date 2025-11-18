from typing import List, Tuple

from indicator.trendline_const import TrendDir
from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineZigZagAtrIndicator(TrendLineIndicator):
    def __init__(self, zigzag_atr_multiplier: float = 1.1):
        super().__init__(trend_type="zigzag_atr")

        self.zigzag_atr_multiplier = zigzag_atr_multiplier

    @staticmethod
    def apply_zigzag_with_atr(trend_type, atr_multiplier, candles: List[Candle]) -> None:
        # Step 1: Find the index of the first candle with a valid ATR
        start_index = next(
            (i for i, c in enumerate(candles) if c.get_indicator('atr') is not None),
            -1
        )
        if start_index == -1 or len(candles) < start_index + 2:
            print("lack atrs")
            return

        # Step 2: Initialize variables starting from the valid point
        first = candles[start_index]
        # Select the more extreme value between high/low as the initial pivot instead of using the close price.
        last_pivot_price = first.high if first.high - first.close >= first.close - first.low else first.low
        trend_dir = None

        candidate_pivot_price = last_pivot_price
        candidate_pivot_idx = start_index

        pivots: List[Tuple[int, float, TrendDir]] = []

        # Step 3: Main loop
        for i in range(start_index + 1, len(candles)):
            c = candles[i]
            atr = c.get_indicator('atr')
            if atr is None:
                continue

            threshold = atr_multiplier * atr
            price = c.close

            # Initial trend determination
            if trend_dir is None:
                delta = price - last_pivot_price
                if abs(delta) >= threshold:
                    trend_dir = TrendDir.UP if delta > 0 else TrendDir.DOWN
                    candidate_pivot_price = price
                    candidate_pivot_idx = i
                continue

            # Update the highest high or check retracement during an uptrend
            if trend_dir == TrendDir.UP:
                if c.high > candidate_pivot_price:
                    candidate_pivot_price = c.high
                    candidate_pivot_idx = i
                elif candidate_pivot_price - c.low >= threshold:
                    pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendDir.TOP))
                    trend_dir = TrendDir.DOWN
                    candidate_pivot_price = c.low
                    candidate_pivot_idx = i

            # Update the lowest low or check retracement during a downtrend
            else:  # TrendDir.DOWN
                if c.low < candidate_pivot_price:
                    candidate_pivot_price = c.low
                    candidate_pivot_idx = i
                elif c.high - candidate_pivot_price >= threshold:
                    pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendDir.BOTTOM))
                    trend_dir = TrendDir.UP
                    candidate_pivot_price = c.high
                    candidate_pivot_idx = i

        # Step 4: Confirm the final pivot
        if trend_dir is not None and candidate_pivot_idx != start_index:
            final_dir = TrendDir.TOP if trend_dir == TrendDir.UP else TrendDir.BOTTOM
            pivots.append((candidate_pivot_idx, candidate_pivot_price, final_dir))

        # Step 5: Apply swing information to candles
        last_offset = 0
        for idx, price, t_dir in pivots:
            fill_dir = TrendDir.UP if t_dir == TrendDir.BOTTOM else TrendDir.DOWN
            for j in range(last_offset, idx):
                candles[j].set_swing_dir(trend_type, fill_dir)
            last_offset = idx + 1

            candles[idx].set_swing_price(trend_type, price)
            candles[idx].set_swing_dir(trend_type, t_dir)

    def calculate_swing_lines(self, symbol, timeframe, end_time, candles) -> None:
        TrendLineZigZagAtrIndicator.apply_zigzag_with_atr(self.trend_type, self.zigzag_atr_multiplier, candles)

class TrendLineZigZagAtrIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('zigzag_atr', swing_color, major_swing_color, trend_color)