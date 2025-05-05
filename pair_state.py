import asyncio
from datetime import datetime, timedelta
from config import EMA_PERIOD, LOG_TO_TERMINAL
from telegram_alert import send_trade_alert
from mt5_bridge import fetch_mt5_candles

active_monitors = {}

def log(pair, msg):
    if LOG_TO_TERMINAL:
        print(f"[{datetime.utcnow()}] [{pair}] {msg}")

async def monitor_pair(bot, chat_id, pair):
    monitor_id = f"{chat_id}_{pair}"
    if monitor_id in active_monitors:
        return
    active_monitors[monitor_id] = True

    log(pair, f"monitor_pair started for chat {chat_id}")
    last_signal_time = None

    while True:
        candles_5m = fetch_mt5_candles(pair, "5min")
        if not candles_5m or len(candles_5m) < EMA_PERIOD:
            await asyncio.sleep(5)
            continue

        latest = candles_5m[0]
        high = float(latest['high'])
        low = float(latest['low'])
        closes = [float(c['close']) for c in candles_5m[:EMA_PERIOD]]
        ema = sum(closes) / EMA_PERIOD
        trend = "up" if float(latest['close']) > ema else "down"
        current_5m_time = latest['datetime']

        log(pair, f"5m Setup: Time={current_5m_time}, Trend={trend}, High={high}, Low={low}, EMA={ema:.5f}")

        if last_signal_time == current_5m_time:
            await asyncio.sleep(5)
            continue

        while True:
            candles_1m = fetch_mt5_candles(pair, "1min")
            if not candles_1m:
                await asyncio.sleep(5)
                continue

            c = candles_1m[0]
            close = float(c['close'])
            candle_time = c['datetime']
            candle_open = datetime.strptime(candle_time, "%Y-%m-%d %H:%M:%S")
            candle_close_time = candle_open + timedelta(minutes=1)

            if datetime.utcnow() < candle_close_time:
                await asyncio.sleep(2)
                continue

            log(pair, f"Checked 1m close={close:.5f} at {candle_time}")

            if trend == "up" and close < low:
                log(pair, f"❌ Invalidated: Trend UP but close < low")
                break
            elif trend == "down" and close > high:
                log(pair, f"❌ Invalidated: Trend DOWN but close > high")
                break

            if trend == "up" and close > high:
                log(pair, f"✅ SELL Signal at {close:.5f}")
                await send_trade_alert(bot, chat_id, pair, "SELL", close)
                last_signal_time = current_5m_time
                break
            elif trend == "down" and close < low:
                log(pair, f"✅ BUY Signal at {close:.5f}")
                await send_trade_alert(bot, chat_id, pair, "BUY", close)
                last_signal_time = current_5m_time
                break

            log(pair, f"Skipped: No breakout")
            await asyncio.sleep(5)