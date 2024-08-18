from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

button_registr = KeyboardButton(text="Регистрация")
button_exrates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")


keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exrates],
    [button_tips, button_finances]
    ], resize_keyboard=True)

