import asyncio, json, os, sys, subprocess
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS_FILE
from pair_state import monitor_pair, active_monitors
from photo_handler import ask_for_photo, handle_photo, handle_photo_action

bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def load_users():
    with open(ALLOWED_USERS_FILE) as f:
        return json.load(f)

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer("Welcome! Use /available, /status, /clear, /usage.")

@dp.message(Command("available"))
async def cmd_available(msg: Message):
    if msg.from_user.id not in load_users():
        return await msg.answer("Not allowed.")
    await msg.answer("Send one or more pairs (comma-separated), e.g.: EURUSD, GBPJPY")

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
        await msg.answer("Monitored:\n" + "\n".join(pairs))
    else:
        await msg.answer("No pairs monitored.")

@dp.message(Command("photos"))
async def photo_command(msg: Message):
    await ask_for_photo(msg)

@dp.message(F.photo)
async def photo_received(msg: Message):
    await handle_photo(msg)

@dp.callback_query(F.data.in_(["photo_add", "photo_cancel"]))
async def photo_response(cb: Message):
    await handle_photo_action(cb)

@dp.message(F.text)
async def handle_pair_input(msg: Message):
    uid = msg.from_user.id
    if uid not in load_users():
        return await msg.answer("Not allowed.")
    pairs = [p.strip().upper() for p in msg.text.split(",") if p.strip()]
    for pair in pairs:
        await msg.answer(f"Monitoring {pair}...")
        asyncio.create_task(monitor_pair(bot, uid, pair))

async def auto_update_and_restart():
    while True:
        process = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if "Already up to date" not in process.stdout:
            print("Update detected. Restarting bot...")
            await bot.session.close()
            os.execv(sys.executable, ['python'] + sys.argv)
        await asyncio.sleep(1)

async def main():
    asyncio.create_task(auto_update_and_restart())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())