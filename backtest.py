from datetime import timedelta, datetime

import pytz

from exchange.crypto_binance import CryptoBinanceExchange
from exchange.util import find_regular_market_candle_time_after, find_regular_market_candle_time_before, \
    timeframe_to_minutes
from indicator.atr import ATRIndicatorDrawer, ATRIndicator
from indicator.fvg import FVGIndicator, FVGIndicatorDrawer

from indicator.rsi import RSIIndicator, RSIIndicatorDrawer
from indicator.ma import MAIndicatorDrawer, MAIndicator
from indicator.trendline_base import TrendLineIndicator, TrendLineIndicatorDrawer
from indicator.trendline_oneway import TrendLineOnewayIndicatorDrawer
from indicator.trendline_zigzag import TrendLineZigZagIndicatorDrawer

from indicator.trendline_zigzag_atr import TrendLineZigZagAtrIndicatorDrawer, TrendLineZigZagAtrIndicator
from indicator.volume import VolumeIndicatorDrawer
from model.symbol import Symbol
from util import fetch_candles, apply_indicators

if __name__ == "__main__":
    mode_ma = 'sma'
    mode_atr = 'sma'

    indicators = [ATRIndicator(period=14, mode=mode_atr), RSIIndicator(period=14), TrendLineZigZagAtrIndicator(1.1),  #TrendLineZigZagIndicator(5), TrendLineOnewayIndicator(),
                  MAIndicator(period=5, mode=mode_ma), MAIndicator(period=20, mode=mode_ma), MAIndicator(period=50, mode=mode_ma), MAIndicator(period=20, mode=mode_ma),
                  FVGIndicator('zigzag_atr', atr_multiplier=0.1, ob_limit_on_trendline=3)] # FVG must come after ATR

    indicator_price_drawers = [
        TrendLineZigZagAtrIndicatorDrawer('blue', 'red', 'red')
        #, TrendLineZigZagIndicatorDrawer('blue', 'red', 'red')
        #, TrendLineOnewayIndicatorDrawer('blue', 'red', 'red')
        #, MAIndicatorDrawer(period=5, color='magenta')
        #, MAIndicatorDrawer(period=20, color='orange')
        , MAIndicatorDrawer(period=50, color='teal')
        , MAIndicatorDrawer(period=200, color='black')
        , FVGIndicatorDrawer(True, True)
    ]

    indicator_drawers = [
        VolumeIndicatorDrawer(),
        RSIIndicatorDrawer(),
        ATRIndicatorDrawer(),
    ]

    is_draw_candle = False

    ticker = "ETH/USDT"
    excd = None

    days_1d = 500

    timeframe = "4h"
    days = 200

    exchange = CryptoBinanceExchange()

    # user custom
    start = datetime.strptime('202501020000', '%Y%m%d%H%M')
    #end = datetime.strptime('202506040000', '%Y%m%d%H%M')
    et_end = datetime.now(pytz.timezone('US/Eastern'))
    end = datetime(et_end.year, et_end.month, et_end.day, et_end.hour, et_end.minute, et_end.second)

    # recalculate candle position
    start = find_regular_market_candle_time_after(exchange, timeframe, start)
    end = find_regular_market_candle_time_before(exchange, timeframe, end)

    # Collect candles by symbol and apply indicators
    candle_dict = {}

    symbol = Symbol(ticker, excd, 'zigzag_atr')
    fetch_candles(symbol, exchange, "1d", datetime.now() - timedelta(days=days_1d))
    if indicators != None and len(indicators) > 0:
        apply_indicators(symbol, "1d", indicators)

    fetch_candles(symbol, exchange, timeframe, datetime.now()-timedelta(days=days))
    if indicators != None and len(indicators) > 0:
        apply_indicators(symbol, timeframe, indicators)

    candles = symbol.get_candles(timeframe)
    for i in range(len(candles)):
        c = candles[i]
        candle_dict[c.timestamp.timestamp()] = (c, i)

    #-- backtest
    dup_table = set()
    cur_time = start
    while True:
        if cur_time.timestamp() in candle_dict:
            # code something
            print (candle_dict[cur_time.timestamp()])

        cur_time += timedelta(minutes=timeframe_to_minutes(timeframe))
        if cur_time > end:
            break

    print (start, end)




