from datetime import datetime

from indicator.trendline_const import TrendDir

class Candle:
    def __init__(self, index: int, timestamp: datetime, open_price: float, close_price: float,
                 low_price: float, high_price: float, volume: float = 0.0):
        self.index = index
        self.timestamp = timestamp
        self.open = open_price
        self.close = close_price
        self.low = low_price
        self.high = high_price
        self.volume = volume
        self.indicators = {}  # Dictionary to store indicator values

    def __repr__(self):
        d = self.timestamp.strftime("%y-%m-%d %H:%M")
        return f"date={d}, o={self.open}, c={self.close}, l={self.low}, h={self.high}, v={self.volume}, inds={self.indicators}"

    def __str__(self):
        d = self.timestamp.strftime("%y-%m-%d %H:%M")
        return f"date={d}, o={self.open}, c={self.close}, l={self.low}, h={self.high}, v={self.volume}, inds={self.indicators}"

    # Set indicator value
    def set_indicator(self, name: str, value):
        self.indicators[name] = value

    # Get indicator value
    def get_indicator(self, name: str):
        return self.indicators.get(name)

    def is_bullish(self):
        return self.open < self.close

    def is_bearish(self):
        return self.open > self.close

    def has_doji(self, max_body_ratio: float = 0.1) -> bool:
        body_size = abs(self.close - self.open)
        total_range = self.high - self.low

        if total_range == 0:
            return False  # If the price is fixed, don't treat it as a doji

        return (body_size / total_range) <= max_body_ratio

    def get_shadow_ratios(self) -> dict:
        body_size = abs(self.close - self.open)
        if body_size == 0:
            body_size = 0.0001  # Prevent division by zero

        upper_shadow = self.high - max(self.open, self.close)
        lower_shadow = min(self.open, self.close) - self.low

        return {
            'upper': upper_shadow / body_size,
            'lower': lower_shadow / body_size
        }

    def has_long_shadow(self, is_upper, min_shadow_body_ratio: float = 1.0, min_shadow_ratio: float = 2.0) -> bool:
        if is_upper:
            return self.has_long_upper_shadow(min_shadow_body_ratio, min_shadow_ratio)
        else:
            return self.has_long_lower_shadow(min_shadow_body_ratio, min_shadow_ratio)

    def has_long_upper_shadow(self, min_shadow_body_ratio: float = 1.0, min_shadow_ratio: float = 2.0) -> bool:
        ratios = self.get_shadow_ratios()
        upper = ratios['upper']
        lower = ratios['lower']

        return (
                upper >= min_shadow_body_ratio and
                (lower == 0 or upper / lower >= min_shadow_ratio)
        )

    def has_long_lower_shadow(self, min_shadow_body_ratio: float = 1.0, min_shadow_ratio: float = 2.0) -> bool:
        ratios = self.get_shadow_ratios()
        upper = ratios['upper']
        lower = ratios['lower']

        return (
                lower >= min_shadow_body_ratio and
                (upper == 0 or lower / upper >= min_shadow_ratio)
        )

    # swing
    def set_swing_dir(self, trend_type: str, value):
        self.set_indicator("swing_dir_" + trend_type, value)

    def get_swing_dir(self, trend_type: str):
        return self.get_indicator("swing_dir_" + trend_type)

    def set_swing_price(self, trend_type: str, value):
        self.set_indicator("swing_price_" + trend_type, value)

    def get_swing_price(self, trend_type: str):
        return self.get_indicator("swing_price_" + trend_type)

    # major swing
    def set_major_swing_dir(self, trend_type: str, value):
        self.set_indicator("major_swing_dir_" + trend_type, value)

    def get_major_swing_dir(self, trend_type: str):
        return self.get_indicator("major_swing_dir_" + trend_type)

    def set_major_swing_price(self, trend_type: str, value):
        self.set_indicator("major_swing_price_" + trend_type, value)

    def get_major_swing_price(self, trend_type: str):
        return self.get_indicator("major_swing_price_" + trend_type)

    def has_major_swing_point(self, trend_type: str):
        return self.get_major_swing_dir(trend_type) == TrendDir.TOP or self.get_major_swing_dir(trend_type) == TrendDir.BOTTOM

    # trend
    def set_trend_dir(self, trend_type: str, value):
        self.set_indicator("trend_dir_" + trend_type, value)

    def get_trend_dir(self, trend_type: str):
        return self.get_indicator("trend_dir_" + trend_type)

    def set_trend_price(self, trend_type: str, value):
        self.set_indicator("trend_price_" + trend_type, value)

    def get_trend_price(self, trend_type: str):
        return self.get_indicator("trend_price_" + trend_type)

    # bos, choch
    def set_major_bos(self, trend_type: str, value):
        self.set_indicator("major_bos_" + trend_type, value)

    def get_major_bos(self, trend_type: str):
        return self.get_indicator("major_bos_" + trend_type)

    def set_major_choch(self, trend_type: str, value):
        self.set_indicator("major_choch_" + trend_type, value)

    def get_major_choch(self, trend_type: str):
        return self.get_indicator("major_choch_" + trend_type)

    def set_major_choch_by(self, trend_type: str, value):
        self.set_indicator("major_choch_by_" + trend_type, value)

    def get_major_choch_by(self, trend_type: str):
        return self.get_indicator("major_choch_by_" + trend_type)
