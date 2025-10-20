from typing import List
from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineZigZagIndicator(TrendLineIndicator):
    def __init__(self, zigzag_deviation_percent: float = 5.0, trend_atr_multiplier: float = 2):
        super().__init__(trend_type="zigzag", trend_atr_multiplier=trend_atr_multiplier)

        self.zigzag_deviation_percent = zigzag_deviation_percent

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        if len(candles) < 2:
            return

        # --- initialize variables ---
        pivots = []  # list to store (index, price, swing_dir) tuples

        last_pivot_price = candles[0].close
        last_pivot_idx = 0
        swing_dir = None

        # temporarily store the current trend extreme candidate
        candidate_pivot_price = last_pivot_price
        candidate_pivot_idx = last_pivot_idx

        # --- main loop ---
        for i in range(1, len(candles)):
            current_price_high = candles[i].high
            current_price_low = candles[i].low

            if swing_dir is None:  # determine initial trend
                # decide whether it breaks upward or downward first
                if (current_price_high - last_pivot_price) / last_pivot_price * 100 >= self.zigzag_deviation_percent:
                    swing_dir = TrendLineIndicator.UP
                    candidate_pivot_price = current_price_high
                    candidate_pivot_idx = i
                elif (last_pivot_price - current_price_low) / last_pivot_price * 100 >= self.zigzag_deviation_percent:
                    swing_dir = TrendLineIndicator.DOWN
                    candidate_pivot_price = current_price_low
                    candidate_pivot_idx = i

            elif swing_dir == TrendLineIndicator.UP:  # uptrend (looking for peak)
                if current_price_high > candidate_pivot_price:
                    # found a higher high, update candidate
                    candidate_pivot_price = current_price_high
                    candidate_pivot_idx = i
                else:
                    # check retracement from peak
                    retrace_pct = (candidate_pivot_price - current_price_low) / candidate_pivot_price * 100
                    if retrace_pct >= self.zigzag_deviation_percent:
                        # confirm peak
                        pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendLineIndicator.TOP))
                        swing_dir = TrendLineIndicator.DOWN  # switch trend
                        last_pivot_price = candidate_pivot_price
                        candidate_pivot_price = current_price_low  # new low candidate
                        candidate_pivot_idx = i

            elif swing_dir == TrendLineIndicator.DOWN:  # downtrend (looking for bottom)
                if current_price_low < candidate_pivot_price:
                    # found a lower low, update candidate
                    candidate_pivot_price = current_price_low
                    candidate_pivot_idx = i
                else:
                    # check retracement from bottom
                    retrace_pct = (current_price_high - candidate_pivot_price) / candidate_pivot_price * 100
                    if retrace_pct >= self.zigzag_deviation_percent:
                        # confirm bottom
                        pivots.append((candidate_pivot_idx, candidate_pivot_price, TrendLineIndicator.BOTTOM))
                        swing_dir = TrendLineIndicator.UP  # switch trend
                        last_pivot_price = candidate_pivot_price
                        candidate_pivot_price = current_price_high  # new high candidate
                        candidate_pivot_idx = i

        # after loop, apply confirmed pivots to candles
        last_offset = 0
        for idx, price, t_dir in pivots:
            for i in range(last_offset, idx):
                self.set_swing_dir(candles[i], TrendLineIndicator.UP if t_dir == TrendLineIndicator.TOP else TrendLineIndicator.DOWN)
            last_offset = idx + 1

            self.set_swing_price(candles[idx], price)
            self.set_swing_dir(candles[idx], t_dir)

class TrendLineZigZagIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, major_swing_color: str, trend_color: str):
        super().__init__('zigzag', swing_color, major_swing_color, trend_color)
