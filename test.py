from typing import List
import matplotlib.pyplot as plt
from candle import Candle
from candle_converter import CandleConverter
from exchange.base import BaseExchange
from exchange.binance import BinanceExchange

from indicator.indicator import Indicator
from indicator.indicator_drawer import IndicatorDrawer
from indicator.rsi import RSIIndicator, RSIIndicatorDrawer
from indicator.ma import MAIndicatorDrawer, MAIndicator
from indicator.atr import ATRIndicatorDrawer, ATRIndicator
from indicator.fvg import FVGIndicatorDrawer, FVGIndicator
from indicator.trend_line import TrendLineIndicator, TrendLineIndicatorDrawer
from indicator.volume import VolumeIndicatorDrawer
from util import apply_indicators, fetch_candles

def plot_candles(indicator_price_drawers: List[IndicatorDrawer], indicator_drawers: List[IndicatorDrawer],
                 candles: List[Candle], draw_candles: bool = True):
    timestamps = [c.timestamp for c in candles]
    opens = [c.open for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    closes = [c.close for c in candles]
    volumes = [c.volume for c in candles]

    # Debug print
    print("Sample values:")
    for i in range(min(5, len(candles))):
        print(f"Candle {i}: high={highs[i]}, low={lows[i]}, close={closes[i]}, "
              f"volume={volumes[i]}")

    # 0 = price chart
    # 1 ~ 1 + len(indicator_drawers) = indicators
    fig, axs = plt.subplots(1 + len(indicator_drawers), 1, figsize=(12, 8), sharex=True,
                            gridspec_kw={'height_ratios': [3] + [1] * len(indicator_drawers)})

    price_ax = axs[0]
    indicators_axs = axs[1:]

    # Candlestick chart
    if draw_candles:
        for i in range(len(candles)):
            color = 'green' if closes[i] >= opens[i] else 'red'
            price_ax.plot([timestamps[i], timestamps[i]], [lows[i], highs[i]], color='black', linewidth=1)
            price_ax.plot([timestamps[i], timestamps[i]], [opens[i], closes[i]], color=color, linewidth=3)

    for drawer in indicator_price_drawers:
        drawer.draw(price_ax, timestamps, opens, closes, lows, highs, volumes, candles)

    price_ax.set_ylabel('Price')
    price_ax.set_title('Candlestick Chart')
    price_ax.grid(True)

    # Indicators
    for i in range(len(indicator_drawers)):
        indicator_drawers[i].draw(indicators_axs[i], timestamps, opens, closes, lows, highs, volumes, candles)

    handles, labels = price_ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    price_ax.legend(by_label.values(), by_label.keys())

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    mode_ma = 'sma'
    mode_atr = 'sma'

    indicators = [ATRIndicator(period=14, mode=mode_atr), RSIIndicator(period=14), TrendLineIndicator(),
                  MAIndicator(period=5, mode=mode_ma), MAIndicator(period=20, mode=mode_ma), MAIndicator(period=50, mode=mode_ma), MAIndicator(period=20, mode=mode_ma),
                  FVGIndicator(atr_multiplier=0.1)] # FVG must come after ATR
    
    indicator_price_drawers = [
        TrendLineIndicatorDrawer('blue')
        , MAIndicatorDrawer(period=5, color='magenta')
    #    , MAIndicatorDrawer(period=20, color='orange')
        , MAIndicatorDrawer(period=50, color='teal')
        , MAIndicatorDrawer(period=200, color='black')
        , FVGIndicatorDrawer()
    ]

    indicator_drawers = [
        VolumeIndicatorDrawer(),
        RSIIndicatorDrawer(),
        ATRIndicatorDrawer(),
    ]

    timeframe = "4h"
    ticker = "BTC/USDT"
    limit = 500
    is_draw_candle = True

    binance = BinanceExchange()
    candles = fetch_candles(binance, ticker, timeframe, limit)

    apply_indicators(indicators, candles)

    # Draw chart
    plot_candles(indicator_price_drawers, indicator_drawers, candles, draw_candles=is_draw_candle)
