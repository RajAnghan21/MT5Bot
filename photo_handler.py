import re
import pytesseract
from PIL import Image
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pair_state import monitor_pair

user_pending_photos = {}

async def ask_for_photo(message: types.Message):
    await message.answer("Send a screenshot with currency pairs.")

async def handle_photo(message: types.Message, bot):
    user_id = message.from_user.id
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path

    filename = f"photo_{user_id}.jpg"
    await bot.download_file(file_path, destination=filename)

    image = Image.open(filename)
    text = pytesseract.image_to_string(image)

    pairs = set(re.findall(r"[A-Z]{3}/[A-Z]{3}", text))
    if not pairs:
        await message.answer("No currency pairs found.")
        return

    user_pending_photos[user_id] = list(pairs)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Add", callback_data="photo_add"),
         InlineKeyboardButton("Cancel", callback_data="photo_cancel")]
    ])
    await message.answer("Detected pairs:\n" + "\n".join(pairs), reply_markup=markup)

async def handle_photo_action(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "photo_add":
        pairs = user_pending_photos.pop(user_id, [])
        for p in pairs:
            await monitor_pair(callback.bot, user_id, p)
        await callback.message.edit_text("Now monitoring:\n" + "\n".join(pairs))
    else:
        await callback.message.edit_text("Cancelled.")
