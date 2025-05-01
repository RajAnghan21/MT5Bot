import re
import pytesseract
from PIL import Image
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pair_state import monitor_pair

router = Router()
user_pending_photos = {}

@router.message(commands=["photos"])
async def ask_photo(message: types.Message):
    await message.answer("Send an image with currency pairs.")

@router.message(content_types=["photo"])
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    photo = message.photo[-1]
    file = await photo.download(destination_dir=".")
    image = Image.open(file.name)
    text = pytesseract.image_to_string(image)
    pairs = set(re.findall(r"[A-Z]{3}/[A-Z]{3}", text))
    if not pairs:
        await message.answer("No valid pairs found.")
        return
    user_pending_photos[user_id] = list(pairs)
    buttons = [[InlineKeyboardButton(text="Add", callback_data="photo_add"),
                InlineKeyboardButton(text="Cancel", callback_data="photo_cancel")]]
    await message.answer("Detected pairs:
" + "\n".join(pairs), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(lambda c: c.data in ["photo_add", "photo_cancel"])
async def handle_action(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "photo_cancel":
        user_pending_photos.pop(user_id, None)
        await callback.message.edit_text("Cancelled.")
    else:
        pairs = user_pending_photos.pop(user_id, [])
        await callback.message.edit_text("Monitoring:
" + "\n".join(pairs))
        for pair in pairs:
            await monitor_pair(callback.bot, user_id, pair)
