from datetime import datetime
async def send_trade_alert(bot, chat_id, pair, direction, price):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"<b>{direction} Signal on {pair}</b>\nEntry: {price}\nTime: {timestamp} UTC\nExpiry: 2 min"
    await bot.send_message(chat_id, msg)
