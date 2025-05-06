import MetaTrader5 as mt5
from datetime import datetime
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

def fetch_mt5_candles(symbol, interval):
    if not mt5.initialize():
        print(f"[{symbol}] ❌ MT5 login failed: {mt5.last_error()}")
        return []

    tf = mt5.TIMEFRAME_M1 if interval == "1min" else mt5.TIMEFRAME_M5
    count = 30 if interval == "1min" else 50
    data = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    mt5.shutdown()

    return [{
        "datetime": datetime.utcfromtimestamp(r['time']).strftime("%Y-%m-%d %H:%M:%S"),
        "open": r['open'], "high": r['high'],
        "low": r['low'], "close": r['close'],
        "volume": r['tick_volume']
    } for r in reversed(data)]