from datetime import datetime, timedelta
from typing import List

from model.candle import Candle
from candle_converter import CandleConverter
from exchange.base import BaseExchange
from indicator.indicator import Indicator
from model.symbol import Symbol


def fetch_candles(symbol, exchange: BaseExchange, timeframe: str, since: datetime) -> List[Candle]:
    converter = CandleConverter()
    raw_data = exchange.fetch_candles(symbol.ticker, timeframe, since, symbol.excd)
    raw_data = sorted(raw_data, key=lambda c: c['timestamp'])

    candles = converter.to_candles(raw_data)
    if len(candles) > 0:
        symbol.set_candles(timeframe, candles)

def apply_indicators(symbol, timeframe, end_time, indicators: List[Indicator]):
    for indicator in indicators:
        candles = symbol.get_candles(timeframe, end_time)
        timestamps = [c.timestamp for c in candles]
        opens = [c.open for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        closes = [c.close for c in candles]
        volumes = [c.volume for c in candles]

        indicator.calculate(symbol, timeframe, end_time, candles, timestamps, opens, closes, lows, highs, volumes)


def to_readable(num, decimals=1):
    """
    Convert a number to a human-readable string.
    1,000 -> '1K', 1,500 -> '1.5K'
    1,000,000 -> '1M', 2,530,000 -> '2.5M'
    1,000,000,000 -> '1B', 1,000,000,000,000 -> '1T', etc.
    Negative numbers are also supported.

    num: number to convert
    decimals: number of decimal places
    """
    # convert all suffixes to uppercase
    suffixes = ['', 'K', 'M', 'B', 'T', 'P', 'E']
    val = float(num)
    idx = 0
    while abs(val) >= 1000 and idx < len(suffixes) - 1:
        idx += 1
        val /= 1000.0

    # format up to the specified number of decimal places
    fmt = f"{val:.{decimals}f}"
    # remove unnecessary .0
    if '.' in fmt:
        fmt = fmt.rstrip('0').rstrip('.')
    return f"{fmt}{suffixes[idx]}"