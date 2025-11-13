from exchange.base import BaseExchange
from typing import List, Dict
from datetime import datetime

import yfinance as yf

# implement Yahoo API (not suitable for real-time use due to latency)
class CryptoYfinanceExchange(BaseExchange):
    def __init__(self):
        pass

    def get_name(self) -> str:
        return 'Yahoo'

    def fetch_candles(self, ticker: str, timeframe: str, since: datetime, excd: str = None) -> List[Dict[str, float]]:
        ticker = ticker.replace('/', '-').replace('USDT', 'USD')
        if timeframe[-1] == 'w':
            timeframe = timeframe[:1] + 'wk'
        elif timeframe[-1] == 'M':
            timeframe = timeframe[:1] + 'mo'

        rt_data = yf.download(
            tickers=ticker,
            period=str((datetime.now() - since).days) + "d",
            interval=timeframe,
            auto_adjust=True,
            ignore_tz=True,
            prepost=False
        )

        if rt_data.empty:
            return []

        df = rt_data.copy()
        df[('xymd', ticker)] = df.index.strftime('%Y%m%d')
        df[('xhms', ticker)] = df.index.strftime('%H%M%S')

        result = [
            {
                "timestamp": datetime.strptime(
                    f"{row[('xymd',ticker)]}{row[('xhms',ticker)].zfill(6)}",
                    "%Y%m%d%H%M%S"
                ),
                "open": float(row[("Open", ticker)]),
                "high": float(row[("High", ticker)]),
                "low": float(row[("Low", ticker)]),
                "close": float(row[("Close", ticker)]),
                "volume": float(row[("Volume", ticker)])
            }
            for row in df.to_dict('records')
            # filter data only after since
            if datetime.strptime(
                f"{row[('xymd',ticker)]}{row[('xhms',ticker)].zfill(6)}",
                "%Y%m%d%H%M%S"
            ) >= since
        ]

        return result
