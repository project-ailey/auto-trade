from datetime import datetime, timedelta
from typing import List

from candle import Candle
from candle_converter import CandleConverter
from exchange.base import BaseExchange
from indicator.indicator import Indicator

def fetch_candles(exchange: BaseExchange, symbol: str, timeframe: str, limit: int, excd: str = None) -> List[Candle]:
    converter = CandleConverter()
    raw_data = exchange.fetch_candles(symbol, timeframe, limit, excd)
    raw_data = sorted(raw_data, key=lambda c: c['timestamp'])
    return converter.to_candles(raw_data)

def apply_indicators(indicators: List[Indicator], candles: List[Candle]):
    for indicator in indicators:
        indicator.calculate(candles)

# Convert timeframe string to seconds
def timeframe_to_seconds(timeframe: str) -> int:
    units = {"m": 60, "h": 3600, "d": 86400, "w": 604800, "M": 2592000}  # week, month added
    num = int(''.join(filter(str.isdigit, timeframe)))
    unit = ''.join(filter(str.isalpha, timeframe))
    return num * units.get(unit, 60)

# Convert timeframe string to minutes
def timeframe_to_minutes(timeframe: str) -> int:
    units = {"m": 1, "h": 60, "d": 1440, "w": 10080, "M": 43200}
    num = int(''.join(filter(str.isdigit, timeframe)))
    unit = ''.join(filter(str.isalpha, timeframe))
    return num * units.get(unit, 1)

def find_regular_market_candle_time_after(exchange: BaseExchange, timeframe: str, time: datetime):
    (market_start_hour,
     market_start_minute,
     regular_market_start_hour,
     regular_market_start_minute,
     regular_market_end_hour,
     regular_market_end_minute) = exchange.get_market_time()

    regular_start = datetime(time.year, time.month, time.day, regular_market_start_hour, regular_market_start_minute)
    regular_end = datetime(time.year, time.month, time.day, regular_market_end_hour, regular_market_end_minute)

    if time >= regular_start and time <= regular_end:   # If it's outside regular trading hours
        cur_time = datetime(time.year, time.month, time.day, market_start_hour, market_start_minute)
        # Find where the included candle is located
        while True:
            next_time = cur_time + timedelta(minutes=timeframe_to_minutes(timeframe))
            if time >= cur_time and time < next_time:
                return cur_time

            cur_time = next_time
    elif time < regular_start:
        return regular_start    # If it's before regular trading hours, move to market open
    elif time > regular_end:
        return regular_start + timedelta(days=1) # Next day market open

def find_regular_market_candle_time_before(exchange: BaseExchange, timeframe: str, time: datetime):
    (market_start_hour,
     market_start_minute,
     regular_market_start_hour,
     regular_market_start_minute,
     regular_market_end_hour,
     regular_market_end_minute) = exchange.get_market_time()

    regular_start = datetime(time.year, time.month, time.day, regular_market_start_hour, regular_market_start_minute)
    regular_end = datetime(time.year, time.month, time.day, regular_market_end_hour, regular_market_end_minute)

    if time >= regular_start and time <= regular_end:   # If it's outside regular trading hours
        cur_time = datetime(time.year, time.month, time.day, market_start_hour, market_start_minute)
        # Find where the included candle is located
        while True:
            next_time = cur_time + timedelta(minutes=timeframe_to_minutes(timeframe))
            if time >= cur_time and time < next_time:
                return cur_time

            cur_time = next_time
    elif time < regular_start:
        return regular_end - timedelta(days=1)  # Previous day market close
    elif time > regular_end:
        return regular_end    # If it's after market close, limit to closing time
