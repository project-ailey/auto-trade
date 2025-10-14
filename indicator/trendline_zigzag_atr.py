from typing import List
from model.candle import Candle

from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer


class TrendLineZigZagAtrIndicator(TrendLineIndicator):
    def __init__(self, zigzag_atr_multiplier: float = 1.1, trend_atr_multiplier: float = 2):
        super().__init__(trend_type="zigzag_atr", trend_atr_multiplier=trend_atr_multiplier)

        self.zigzag_atr_multiplier = zigzag_atr_multiplier

    def calculate_swing_lines(self, candles: List[Candle]) -> None:
        TrendLineIndicator.apply_zigzag_with_atr('swing_dir_' + self.trend_type, 'swing_price_' + self.trend_type, self.zigzag_atr_multiplier, candles)

class TrendLineZigZagAtrIndicatorDrawer(TrendLineIndicatorDrawer):
    def __init__(self, swing_color: str, trend_color: str):
        super().__init__('zigzag_atr', swing_color, trend_color)