from datetime import timedelta, datetime

import pytz

from exchange.binance import CryptoBinanceExchange
from indicator.atr import ATRIndicatorDrawer, ATRIndicator
from indicator.fvg import FVGIndicator, FVGIndicatorDrawer

from indicator.rsi import RSIIndicator, RSIIndicatorDrawer
from indicator.ma import MAIndicatorDrawer, MAIndicator
from indicator.trend_line import TrendLineIndicator, TrendLineIndicatorDrawer
from indicator.volume import VolumeIndicatorDrawer
from util import fetch_candles, apply_indicators, find_regular_market_candle_time_after, \
    find_regular_market_candle_time_before, timeframe_to_minutes

if __name__ == "__main__":
    mode_ma = 'sma'
    mode_atr = 'ema'

    indicators = [ATRIndicator(period=14, mode=mode_atr), RSIIndicator(period=14), TrendLineIndicator(),
                  MAIndicator(period=5, mode=mode_ma), MAIndicator(period=20, mode=mode_ma), MAIndicator(period=50, mode=mode_ma), MAIndicator(period=20, mode=mode_ma),
                  FVGIndicator('zigzag', atr_multiplier=0.1)] # FVG must come after ATR

    indicator_price_drawers = [
        TrendLineIndicatorDrawer('blue')
        , MAIndicatorDrawer(period=5, color='magenta')
        , MAIndicatorDrawer(period=50, color='teal')
        , MAIndicatorDrawer(period=200, color='black')
        , FVGIndicatorDrawer()
    ]

    indicator_drawers = [
        VolumeIndicatorDrawer(),
        RSIIndicatorDrawer(),
        ATRIndicatorDrawer(),
    ]

    timeframe = "1d"
    ticker = "ETH/USDT"
    limit = 300
    is_draw_candle = True

    binance = CryptoBinanceExchange()
    candles = fetch_candles(binance, ticker, timeframe, limit)

    apply_indicators(indicators, candles)

    #--------------------------------------------------
    # backtest
    candle_dict = {}
    for c in candles:
        candle_dict[c.timestamp.timestamp()] = c

    # user custom
    start = datetime.strptime('202505300000', '%Y%m%d%H%M')
    et_end = datetime.now(pytz.timezone('US/Eastern'))
    end = datetime(et_end.year, et_end.month, et_end.day, et_end.hour, et_end.minute, et_end.second)

    # recalculate candle position
    start = find_regular_market_candle_time_after(binance, timeframe, start)
    end = find_regular_market_candle_time_before(binance, timeframe, end)

    # run
    cur_time = start
    while True:
        if cur_time.timestamp() in candle_dict:
            # code something
            print (candle_dict[cur_time.timestamp()])

        cur_time += timedelta(minutes=timeframe_to_minutes(timeframe))
        if cur_time > end:
            break

    print (start, end)




