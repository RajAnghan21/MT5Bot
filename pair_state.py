import asyncio
from api_manager import fetch_candles
from config import EMA_PERIOD
from telegram_alert import send_trade_alert

active_monitors = {}

async def monitor_pair(bot, chat_id, pair):
    monitor_id = f"{chat_id}_{pair}"
    if monitor_id in active_monitors:
        return
    active_monitors[monitor_id] = True

    while True:
        candles_5m = await fetch_candles(pair, "5min")
        if not candles_5m or len(candles_5m) < EMA_PERIOD:
            await asyncio.sleep(5)
            continue
        latest = candles_5m[0]
        high = float(latest['high'])
        low = float(latest['low'])
        closes = [float(c['close']) for c in candles_5m[:EMA_PERIOD]]
        ema = sum(closes) / EMA_PERIOD
        trend = "up" if float(latest['close']) > ema else "down"

        while True:
            candles_1m = await fetch_candles(pair, "1min")
            if not candles_1m:
                await asyncio.sleep(5)
                continue
            close = float(candles_1m[0]['close'])
            if trend == "up" and close > high:
                await send_trade_alert(bot, chat_id, pair, "BUY", close)
                break
            elif trend == "down" and close < low:
                await send_trade_alert(bot, chat_id, pair, "SELL", close)
                break
            await asyncio.sleep(5)
