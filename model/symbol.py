from datetime import datetime
from typing import Dict, List, Optional, Any

from indicator.trendline_const import TrendDir
from model.candle import Candle


class Symbol:
    def __init__(self, ticker: str, excd: str):
        self.ticker = ticker
        self.excd = excd
        self.candle_list: Dict[str, List[Candle]] = {}
        self.candle_table: Dict[str, Dict[int, tuple[Candle, int]]] = {}

    def set_candles(self, timeframe: str, candles: List[Candle]):
        self.candle_list[timeframe] = candles
        self.candle_table[timeframe] = {}
        for i in range(len(candles)):
            c = candles[i]
            self.candle_table[timeframe][int(c.timestamp.timestamp())] = (c, i)

    def get_candles(self, timeframe: str) -> Optional[List[Candle]]:
        return self.candle_list.get(timeframe)

    def get_candle(self, timeframe: str, candle_time: datetime) -> Optional[Candle]:
        if timeframe in self.candle_table:
            if int(candle_time.timestamp()) in self.candle_table.get(timeframe):
                return self.candle_table.get(timeframe).get(int(candle_time.timestamp()))[0]
            else:
                return None
        else:
            return None

    def get_candle_index(self, timeframe: str, candle_time: datetime) -> int:
        if timeframe in self.candle_table:
            if int(candle_time.timestamp()) in self.candle_table.get(timeframe):
                return self.candle_table.get(timeframe).get(int(candle_time.timestamp()))[1]
            else:
                return -1
        else:
            return -1

    # swing
    def get_prev_swing_high(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if c.get_swing_dir(trend_type) == TrendDir.TOP:
                return c
        return candles[0] if offset_index > 0 and len(candles) > 0 else None

    def get_prev_swing_low(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if c.get_swing_dir(trend_type) == TrendDir.BOTTOM:
                return c
        return candles[0] if offset_index > 0 and len(candles) > 0 else None

    def get_next_swing_high(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if c.get_swing_dir(trend_type) == TrendDir.TOP:
                return c
        return None

    def get_next_swing_low(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if c.get_swing_dir(trend_type) == TrendDir.BOTTOM:
                return c
        return None

    def get_prev_swing_swing_point(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if (c.get_swing_dir(trend_type) == TrendDir.TOP) or (c.get_swing_dir(trend_type) == TrendDir.BOTTOM):
                return c
        return None

    def get_next_swing_point(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_swing_dir(trend_type) == TrendDir.TOP) or (c.get_swing_dir(trend_type) == TrendDir.BOTTOM):
                return c
        return None

    # major swing
    def get_prev_major_swing_high(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if c.get_major_swing_dir(trend_type) == TrendDir.TOP:
                return c
        return candles[0] if offset_index > 0 and len(candles) > 0 else None

    def get_prev_major_swing_low(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if c.get_major_swing_dir(trend_type) == TrendDir.BOTTOM:
                return c
        return candles[0] if offset_index > 0 and len(candles) > 0 else None

    def get_next_major_swing_high(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if c.get_major_swing_dir(trend_type) == TrendDir.TOP:
                return c
        return None

    def get_next_major_swing_low(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if c.get_major_swing_dir(trend_type) == TrendDir.BOTTOM:
                return c
        return None

    def get_prev_major_swing_point(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index - 1, -1, -1):
            c = candles[i]
            if (c.get_major_swing_dir(trend_type) == TrendDir.TOP) or (c.get_major_swing_dir(trend_type) == TrendDir.BOTTOM):
                return c
        return None

    def get_next_major_swing_point(self, timeframe: str, trend_type: str, offset_index: int) -> Optional[Candle]:
        candles = self.get_candles(timeframe)
        for i in range(offset_index + 1, len(candles), 1):
            c = candles[i]
            if (c.get_major_swing_dir(trend_type) == TrendDir.TOP) or (c.get_major_swing_dir(trend_type) == TrendDir.BOTTOM):
                return c
        return None

    def find_high_and_low_between_candles(self, timeframe, start, end):
        low = 999999999999999
        high = -1
        for i in range(start, end + 1):
            if self.candle_list[timeframe][i].high > high:
                high = self.candle_list[timeframe][i].high
            if self.candle_list[timeframe][i].low < low:
                low = self.candle_list[timeframe][i].low

        return (low, high)
