from typing import Dict, List, Optional, Any

from indicator.trendline_base import TrendLineIndicator
from model.candle import Candle


class Symbol:
    def __init__(self, ticker: str, excd: str, ref_trend_type: str = "zigzag"):
        self.ticker = ticker
        self.excd = excd
        self.ref_trend_type = ref_trend_type
        self.candle_groups: Dict[str, List[Candle]] = {}

    def add_candles(self, timeframe: str, candles: List[Candle]):
        self.candle_groups[timeframe] = candles

    def get_candles(self, timeframe: str) -> Optional[List[Candle]]:
        return self.candle_groups.get(timeframe)

    def get_prev_swing_high(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_swing_high(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_prev_swing_low(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_swing_low(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_next_swing_high(self, current_index, timeframe):
        return TrendLineIndicator.get_next_swing_high(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_next_swing_low(self, current_index, timeframe):
        return TrendLineIndicator.get_next_swing_low(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_prev_swing_swing_point(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_swing_swing_point(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_next_swing_swing_point(self, current_index, timeframe):
        return TrendLineIndicator.get_next_swing_swing_point(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_prev_trend_high(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_trend_high(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_prev_trend_low(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_trend_low(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_prev_trend_swing_point(self, current_index, timeframe):
        return TrendLineIndicator.get_prev_trend_swing_point(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def get_next_trend_swing_point(self, current_index, timeframe):
        return TrendLineIndicator.get_next_trend_swing_point(self.ref_trend_type, current_index, self.get_candles(timeframe))

    def find_high_and_low_between_candles(self, start, end, timeframe):
        low = 999999999999999
        high = -1
        for i in range(start, end + 1):
            if self.candle_groups[timeframe][i].high > high:
                high = self.candle_groups[timeframe][i].high
            if self.candle_groups[timeframe][i].low < low:
                low = self.candle_groups[timeframe][i].low

        return (low, high)
