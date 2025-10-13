from datetime import datetime, timedelta
from typing import List

from model.candle import Candle
from candle_converter import CandleConverter
from exchange.base import BaseExchange
from indicator.indicator import Indicator
from model.symbol import Symbol


def fetch_candles(symbol, exchange: BaseExchange, timeframe: str, since: datetime, indicators: List[Indicator]) -> List[Candle]:
    converter = CandleConverter()
    raw_data = exchange.fetch_candles(symbol.ticker, timeframe, since, symbol.excd)
    raw_data = sorted(raw_data, key=lambda c: c['timestamp'])

    candles = converter.to_candles(raw_data)
    if len(candles) > 0:
        symbol.add_candles(timeframe, candles)

    if indicators != None and len(indicators) > 0:
        apply_indicators(symbol, timeframe, indicators)

def apply_indicators(symbol, timeframe, indicators: List[Indicator]):
    for indicator in indicators:
        indicator.calculate(symbol, timeframe)
