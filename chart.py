import time
from datetime import timedelta, datetime
from functools import partial
from typing import List
import matplotlib.pyplot as plt

from exchange.crypto_yfinance import CryptoYfinanceExchange
from exchange.util import find_regular_market_candle_time_after, timeframe_to_minutes
from indicator.ma_daily import MADailyIndicator, MADailyIndicatorDrawer
from indicator.pdarray import PDArrayIndicator, PDArrayIndicatorDrawer
from indicator.trendline_oneway import TrendLineOnewayIndicatorDrawer, TrendLineOnewayIndicator
from indicator.trendline_zigzag import TrendLineZigZagIndicatorDrawer, TrendLineZigZagIndicator
from model.candle import Candle
from exchange.crypto_binance import CryptoBinanceExchange
from indicator.atr import ATRIndicatorDrawer, ATRIndicator
 
from indicator.indicator_drawer import IndicatorDrawer
from indicator.rsi import RSIIndicator, RSIIndicatorDrawer
from indicator.ma import MAIndicatorDrawer, MAIndicator
from indicator.trendline_zigzag_atr import TrendLineZigZagAtrIndicator, TrendLineZigZagAtrIndicatorDrawer
from indicator.volume import VolumeIndicatorDrawer
from model.symbol import Symbol
from util import apply_indicators, fetch_candles, to_readable
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import List

def plot_candles(exchange, symbol, timeframe: str, end_time: datetime, indicators, indicator_price_drawers: List, indicator_drawers: List,
                 draw_candles: bool = True, draw_candle_indice: bool = True):
    root = tk.Tk()
    root.title("Chart Viewer")
    root.state("zoomed")

    # main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # button frame on bottom
    btn_frame = tk.Frame(root)
    btn_frame.pack(side="bottom")

    # consist figure and subplots
    fig = Figure(figsize=(12, 8))
    axs = fig.subplots(1 + len(indicator_drawers), 1, sharex=True,
                       gridspec_kw={'height_ratios': [3] + [1] * len(indicator_drawers)})

    # connect figure to tkinter
    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side="top", fill="both", expand=True)

    helper_object = {
        'end_time': end_time,
        'vlines': [],
        'last_vline_x': None,
        'vline_info': None,
        'hline': None,
        'last_hline_y': None,
    }

    candles = symbol.get_candles(timeframe, None)
    indexes = list(range(len(candles)))
    timestamps = [c.timestamp for c in candles]
    opens = [c.open for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    closes = [c.close for c in candles]
    volumes = [c.volume for c in candles]

    def draw_plot():
        price_ax = axs[0]
        indicators_axs = axs[1:]

        for ax in axs:
            ax.clear()

        if draw_candles:
            for i in range(len(candles)):
                is_visible = helper_object['end_time'] == None or candles[i].timestamp <= helper_object['end_time']
                color = 'green' if closes[i] >= opens[i] else 'red'
                if draw_candle_indice:
                    y = highs[i] * 1.001
                    price_ax.text(indexes[i], y, str(i), ha='center', va='bottom', fontsize=6, color='black', visible=is_visible)

                price_ax.plot([indexes[i], indexes[i]], [lows[i], highs[i]], color='black', linewidth=1, visible=is_visible)
                price_ax.plot([indexes[i], indexes[i]], [opens[i], closes[i]], color=color, linewidth=3, visible=is_visible)

        for drawer in indicator_price_drawers:
            drawer.draw(symbol, timeframe, helper_object['end_time'], price_ax, indexes, candles, timestamps, opens, closes, lows, highs, volumes)

        price_ax.set_ylabel('Price')
        ticker = f"{symbol.ticker}.{symbol.excd}" if symbol.excd else symbol.ticker
        price_ax.set_title(f'{ticker} ({timeframe}) in {exchange.get_name()}')

        new_xticks = list(range(0, len(candles) - 1, max(int(len(candles) / 10), 1)))
        new_xticks.append(len(candles) - 1)
        new_xtick_labels = [timestamps[t] for t in new_xticks]

        price_ax.set_xticks(new_xticks)
        price_ax.set_xticklabels(new_xtick_labels, rotation=45)

        for i, drawer in enumerate(indicator_drawers):
            drawer.draw(symbol, timeframe, helper_object['end_time'], indicators_axs[i], indexes, candles, timestamps, opens, closes, lows, highs, volumes)

        handles, labels = price_ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        price_ax.legend(by_label.values(), by_label.keys())
        price_ax.grid(True)

        # vertical line
        for ax in axs:
            # If last_x is None, hide it; if it has a value, draw the line at that position
            if helper_object['last_vline_x'] is None:
                v = ax.axvline(x=0, color='gray', linestyle='--', visible=False)
            else:
                v = ax.axvline(x=helper_object['last_vline_x'], color='gray', linestyle='--', visible=True)
            helper_object['vlines'].append(v)

        # price line
        if helper_object['last_hline_y'] is None:
            v = price_ax.axhline(y=opens[0], color='gray', linestyle='--', visible=False)
        else:
            v = price_ax.axhline(y=helper_object['last_hline_y'], color='gray', linestyle='--', visible=True)
        helper_object['hline'] = v

        # vertical line info
        helper_object['vline_info'] = axs[0].annotate(
            "",
            xy=(0, 0),
            xytext=(20, -20),
            textcoords="offset points",
            ha="left",
            va="top",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                edgecolor="black",
                alpha=0.8
            ),
            visible=False
        )

        fig.tight_layout()

        canvas.draw()

    def initial_draw():
        root.after(100, draw_plot)  # Draw once more after the window is fully rendered

    def move_next_candle(size):
        if helper_object['end_time'] == None:
            return

        curr_candle = symbol.get_candle_by_candle_time(timeframe, helper_object['end_time'])
        next_candle = symbol.get_candle_by_index(timeframe, curr_candle.index + size)

        for i in range(curr_candle.index + 1):
            candles[i].indicators = {}

        if curr_candle.index + size < 0:
            next_candle = candles[0]
        elif curr_candle.index + size >= len(candles):
            next_candle = candles[len(candles)-1]

        helper_object['end_time'] = next_candle.timestamp

        if indicators != None and len(indicators) > 0:
            apply_indicators(symbol, timeframe, helper_object['end_time'], indicators)
        draw_plot()

    # Connect button functionality and initialize the plot
    jump_list = [-20,-10,-5,-1,+1,+5,+10,+20]
    for j in jump_list:
        btn = tk.Button(btn_frame, text=str(j), padx=20)
        btn.pack(side="left")
        btn.config(command=partial(move_next_candle, j))

    initial_draw()

    def on_mouse_move(event):
        if event.inaxes not in axs or event.xdata is None:
            return

        # 1) Convert xdata - index
        idx = int(round(event.xdata))
        idx = max(0, min(idx, len(timestamps) - 1))

        snap_x = idx

        # 1) Update last_x
        helper_object['last_vline_x'] = snap_x
        # 2) update vlines position only & make it visible
        for v in helper_object['vlines']:
            v.set_xdata([snap_x])
            v.set_visible(True)

        ymin, ymax = axs[0].get_ylim()
        y = min(max(event.ydata, ymin), ymax)
        helper_object['last_hline_y'] = y

        if helper_object['hline'] != None:
            helper_object['hline'].set_ydata([event.ydata])
            helper_object['hline'].set_visible(True)

        # 2) Update info_annot
        helper_object['vline_info'].xy = (snap_x, event.ydata)

        open_rate = ((opens[idx]-closes[idx-1])/closes[idx-1]) * 100
        close_rate = ((closes[idx]-closes[idx-1])/closes[idx-1]) * 100
        low_rate = ((lows[idx]-closes[idx-1])/closes[idx-1]) * 100
        high_rate = ((highs[idx] - closes[idx - 1]) / closes[idx - 1]) * 100
        volume_rate = (1+((volumes[idx] - volumes[idx - 1]) / volumes[idx - 1])) * 100
        current_price_rate = ((event.ydata-closes[idx-1])/closes[idx-1]) * 100

        text = f"{timestamps[idx]:%Y/%m/%d (%a) %H:%M}\n\nOpen: {opens[idx]:,.2f} ({open_rate:.2f}%)\nHigh: {highs[idx]:,.2f} ({high_rate:.2f}%)\nLow: {lows[idx]:,.2f} ({low_rate:.2f}%)\nClose: {closes[idx]:,.2f} ({close_rate:.2f}%)\nVolume: {volumes[idx]:,.0f} ({volume_rate:.2f}%)\n\nCurrent Price: {event.ydata:,.2f} ({current_price_rate:.2f}%)"
        helper_object['vline_info'].set_text(text)
        helper_object['vline_info'].set_visible(timestamps[idx] <= helper_object['end_time'])

        canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", on_mouse_move)

    root.mainloop()

if __name__ == "__main__":
    mode_ma = 'sma'
    mode_atr = 'sma'
    main_trend_type = "zigzag_atr"

    is_draw_candle = True
    is_draw_candle_index = True

    days_1d = 500
    now = datetime.now()
    now_day_only = datetime(now.year, now.month, now.day, 0,0, 0)

    timeframe = "1d"    # tf support - m, h, d, w, M
    ticker = "BTC/USDT"
    days = 120
    excd = None
    #exchange = CryptoBinanceExchange()
    exchange = CryptoYfinanceExchange()
    #end_time = find_regular_market_candle_time_after(exchange, timeframe, now_day_only - timedelta(days=days))
    end_time = now_day_only

    indicators = [ATRIndicator(period=14, mode=mode_atr), RSIIndicator(period=14),
                  TrendLineZigZagAtrIndicator(1),
                  #TrendLineZigZagIndicator(5),
                  #TrendLineOnewayIndicator(),
                  MAIndicator(period=5, mode=mode_ma), MAIndicator(period=20, mode=mode_ma),
                  MAIndicator(period=50, mode=mode_ma), MAIndicator(period=200, mode=mode_ma),
                  MADailyIndicator(period=10, mode=mode_ma), MADailyIndicator(period=20, mode=mode_ma),
                  PDArrayIndicator(main_trend_type, fvg_atr_multiplier=0.3),
                  ]  # FVG must come after ATR

    indicator_price_drawers = [
        TrendLineZigZagAtrIndicatorDrawer('blue', 'red', None),
        #TrendLineZigZagIndicatorDrawer('blue', 'red', None),
        #TrendLineOnewayIndicatorDrawer('blue', 'red', 'magenta'),
        #MAIndicatorDrawer(period=5, color='magenta'),
        #MAIndicatorDrawer(period=20, color='orange'),
        MAIndicatorDrawer(period=50, color='teal'),
        MAIndicatorDrawer(period=200, color='black'),
        MADailyIndicatorDrawer(period=10, color='deepskyblue'),
        MADailyIndicatorDrawer(period=20, color='orange'),
        PDArrayIndicatorDrawer(False, True),
    ]

    indicator_drawers = [
        VolumeIndicatorDrawer(),
        RSIIndicatorDrawer(),
        ATRIndicatorDrawer(),
    ]

    symbol = Symbol(ticker, excd)
    fetch_candles(symbol, exchange, timeframe, now_day_only - timedelta(days=days))
    if indicators != None and len(indicators) > 0:
        apply_indicators(symbol, timeframe, end_time, indicators)

    # Draw chart
    plot_candles(exchange, symbol, timeframe, end_time, indicators, indicator_price_drawers, indicator_drawers, draw_candles=is_draw_candle, draw_candle_indice=is_draw_candle_index)
