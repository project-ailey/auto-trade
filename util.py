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
        symbol.add_candles(timeframe, candles)

def apply_indicators(symbol, timeframe, indicators: List[Indicator]):
    for indicator in indicators:
        candles = symbol.get_candles(timeframe)
        timestamps = [c.timestamp for c in candles]
        opens = [c.open for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        closes = [c.close for c in candles]
        volumes = [c.volume for c in candles]

        indicator.calculate(symbol, timeframe, timestamps, opens, closes, lows, highs, volumes)
