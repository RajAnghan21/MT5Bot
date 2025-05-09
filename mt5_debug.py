from mt5_bridge import fetch_mt5_candles

pairs = [
    "EURUSD", "AUDCAD", "AUDCHF", "AUDJPY", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY",
    "EURAUD", "EURCAD", "EURCHF", "EURGBP", "EURJPY", "GBPAUD", "GBPCAD", "GBPCHF",
    "GBPJPY", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"
]

timeframes = ["1min", "5min"]

print("Starting MT5 candle fetch test...\n")

for pair in pairs:
    symbol = pair + "m"
    print(f"Checking {symbol}:")

    for tf in timeframes:
        candles = fetch_mt5_candles(symbol, tf)
        if candles and len(candles) > 0:
            print(f"✅ {tf} candles fetched. First entry: {candles[0]}")
        else:
            print(f"❌ No {tf} candle data returned.")
    print("-" * 40)
