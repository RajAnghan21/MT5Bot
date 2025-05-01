import asyncio, json
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS_FILE
from pair_state import monitor_pair, active_monitors
from photo_handler import router as photo_router

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(photo_router)

def load_users():
    with open(ALLOWED_USERS_FILE) as f:
        return json.load(f)

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer("Welcome! Use /available, /status, /usage, /clear or /photos.")

@dp.message(Command("available"))
async def cmd_available(msg: Message):
    if msg.from_user.id not in load_users():
        return await msg.answer("Not allowed.")
    await msg.answer("Send one or more pairs (comma-separated), e.g.: EUR/USD, GBP/JPY")

@dp.message(Command("clear"))
async def cmd_clear(msg: Message):
    uid = msg.from_user.id
    keys = [k for k in active_monitors if k.startswith(f"{uid}_")]
    for k in keys:
        del active_monitors[k]
    await msg.answer("All monitoring sessions cleared.")

@dp.message(Command("usage"))
async def cmd_usage(msg: Message):
    try:
        with open("api_usage.txt") as f: count = f.read().strip()
    except: count = "0"
    await msg.answer(f"API Calls: {count}")

@dp.message(Command("status"))
async def cmd_status(msg: Message):
    uid = msg.from_user.id
    pairs = [k.split("_")[1] for k in active_monitors if k.startswith(f"{uid}_")]
    if pairs:
        await msg.answer("Monitored:
" + "\n".join(pairs))
    else:
        await msg.answer("No pairs monitored.")

@dp.message(F.text)
async def handle_input(msg: Message):
    uid = msg.from_user.id
    if uid not in load_users():
        return await msg.answer("Not allowed.")
    pairs = [p.strip().upper() for p in msg.text.split(",") if p.strip()]
    for pair in pairs:
        await msg.answer(f"Monitoring {pair}...")
        asyncio.create_task(monitor_pair(bot, uid, pair))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
