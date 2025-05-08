import asyncio, json, os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS_FILE
from pair_state import monitor_pair, active_monitors, monitor_tasks, subscribed_users
from payout_scraper import fetch_payouts

bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def load_users():
    with open(ALLOWED_USERS_FILE) as f:
        return json.load(f)

async def payout_monitor_task():
    await asyncio.sleep(5)
    print("[PAYOUT] Auto payout monitor started.")
    while True:
        try:
            valid_pairs = await fetch_payouts()
            print("[PAYOUT] Live pairs:", valid_pairs)

            for pair in valid_pairs:
                clean_pair = pair.replace("/", "")
                monitor_id = f"global_{clean_pair}"
                if monitor_id not in active_monitors:
                    print(f"[PAYOUT] Adding {monitor_id}")
                    active_monitors[monitor_id] = True
                    asyncio.create_task(monitor_pair(bot, "global", clean_pair))

            for monitor_id in list(active_monitors):
                if not monitor_id.startswith("global_"):
                    continue
                pair_code = monitor_id.split("_")[1]
                reconstructed = pair_code[:3] + "/" + pair_code[3:]
                if reconstructed not in valid_pairs:
                    print(f"[PAYOUT] Removing {monitor_id}")
                    if monitor_id in monitor_tasks:
                        monitor_tasks[monitor_id].cancel()
                        monitor_tasks.pop(monitor_id, None)
                    active_monitors.pop(monitor_id, None)
        except Exception as e:
            print(f"[PAYOUT] Monitor error: {e}")
        await asyncio.sleep(60)

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
    "👋 Hello, Trader!\n\n"
    "Welcome to the FX Signal Bot — your personal assistant for identifying high-potential forex trade opportunities.\n\n"
    "Use the following commands to get started:\n"
    "/startbot – Begin receiving live trade alerts\n"
    "/stopbot – Stop receiving alerts anytime\n"
    "/status – See your current signal status\n"
    "/pairs – View active analyzing pairs\n"
    "/help – Show all available commands\n\n"
    "💡 *Risk Management Tip:*\n"
    "Never risk more than 1–2% of your capital per trade. Consistency and discipline are key to long-term success.\n\n"
    "Wishing you confident and informed trading! 📈💼"
)


@dp.message(Command("startbot"))
async def cmd_startbot(msg: Message):
    uid = msg.from_user.id
    if uid not in load_users():
        return await msg.answer("❌ Not allowed.")
    subscribed_users.add(uid)
    await msg.answer("✅ You will now receive trade signals.")

@dp.message(Command("stopbot"))
async def cmd_stopbot(msg: Message):
    uid = msg.from_user.id
    subscribed_users.discard(uid)
    await msg.answer("⛔ You will no longer receive trade signals.")

@dp.message(Command("status"))
async def cmd_status(msg: Message):
    uid = msg.from_user.id
    if uid in subscribed_users:
        await msg.answer("🔔 You are subscribed to receive signals.")
    else:
        await msg.answer("🔕 You are not receiving signals. Use /startbot to subscribe.")

@dp.message(Command("pairs"))
async def cmd_pairs(msg: Message):
    global_pairs = [k.split("_")[1] for k in active_monitors if k.startswith("global_")]
    if not global_pairs:
        await msg.answer("🔍 No pairs are currently being analyzed.")
    else:
        await msg.answer("📡 Currently analyzing:" + "\n".join(global_pairs))

@dp.message(Command("help"))
async def cmd_help(msg: Message):
    help_text = (
        "🤖 *Available Commands:*\n"
        "/startbot - Start receiving signals\n"
        "/stopbot - Stop receiving signals\n"
        "/status - Check subscription status\n"
        "/pairs - View active analyzing pairs"
    )
    await msg.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("allow"))
async def cmd_allow(msg: Message):
    if msg.from_user.id != 777715557:
        return await msg.answer("❌ Not authorized.")
    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Usage: /allow <user_id>")
    user_id = int(parts[1])
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(ALLOWED_USERS_FILE, "w") as f:
            json.dump(users, f)
        await msg.answer(f"✅ Allowed user {user_id}")
    else:
        await msg.answer(f"⚠️ User {user_id} already allowed.")

@dp.message(Command("block"))
async def cmd_block(msg: Message):
    if msg.from_user.id != 777715557:
        return await msg.answer("❌ Not authorized.")
    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Usage: /block <user_id>")
    user_id = int(parts[1])
    users = load_users()
    if user_id in users:
        users.remove(user_id)
        with open(ALLOWED_USERS_FILE, "w") as f:
            json.dump(users, f)
        await msg.answer(f"⛔ Blocked user {user_id}")
    else:
        await msg.answer(f"⚠️ User {user_id} is not in the list.")

@dp.message(Command("users"))
async def cmd_users(msg: Message):
    if msg.from_user.id != 777715557:
        return await msg.answer("❌ Not authorized.")
    users = load_users()
    if users:
        await msg.answer("👥 Allowed Users:" + "\n".join(map(str, users)))
    else:
        await msg.answer("⚠️ No users currently allowed.")

async def main():
    asyncio.create_task(payout_monitor_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "👋 Hello, Trader!\n\n"
        "Welcome to the FX Signal Bot — your personal assistant for identifying high-potential forex trade opportunities.\n\n"
        "Use the following commands to get started:\n"
        "/startbot – Begin receiving live trade alerts\n"
        "/stopbot – Stop receiving alerts anytime\n"
        "/status – See your current signal status\n"
        "/pairs – View active analyzing pairs\n"
        "/help – Show all available commands\n\n"
        "💡 *Risk Management Tip:*\n"
        "Never risk more than 1–2% of your capital per trade. Consistency and discipline are key to long-term success.\n\n"
        "Wishing you confident and informed trading! 📈💼"
    )
