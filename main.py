from config import TOKEN, RATE_API
import keyboards as kb
from tips import tips_list

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import logging
import sqlite3
import requests
import random

conn = sqlite3.connect('users.db')




bot = Bot(TOKEN)
dp = Dispatcher()

class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

@dp.message(CommandStart())
async def start(message: Message):
   await message.answer("Привет! Я ваш финансовый помощник. Выберите одну из опций в меню:",
                        reply_markup=kb.keyboard)

@dp.message(F.text == "Регистрация")
async def register(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer("Вы уже зарегистрированы!")
    cursor.close()

@dp.message(F.text == "Курс валют")
async def exrates(message: Message):
    url = f'https://v6.exchangerate-api.com/v6/{RATE_API}/latest/USD'
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']

        euro_to_rub = usd_to_rub / eur_to_usd

        await message.answer(f"1 USD - {usd_to_rub:.2f}  RUB\n"
                             f"1 EUR - {euro_to_rub:.2f}  RUB")
    except:
        await message.answer("Произошла ошибка")

@dp.message(F.text == "Советы по экономии")
async def tips(message: Message):
    tip = random.choice(tips_list)
    await message.answer(tip)

@dp.message(F.text == "Личные финансы")
async def finances(message: Message, state: FSMContext):
    await message.answer("Выберите категорию:")
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")

@dp.message(FinancesForm.category1)
async def category1(message: Message, state: FSMContext):
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите сумму расходов для первой категории:")


@dp.message(FinancesForm.expenses1)
async def expenses1(message: Message, state: FSMContext):
    await state.update_data(expenses1=float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов:")

@dp.message(FinancesForm.category2)
async def category2(message: Message, state: FSMContext):
    await state.update_data(category2=message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите сумму расходов для второй категории:")

@dp.message(FinancesForm.expenses2)
async def expenses2(message: Message, state: FSMContext):
    await state.update_data(expenses2=float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов:")

@dp.message(FinancesForm.category3)
async def category3(message: Message, state: FSMContext):
    await state.update_data(category3=message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите сумму расходов для третьей категории:")

@dp.message(FinancesForm.expenses3)
async def finances(message: Message, state: FSMContext):
    await state.update_data(expenses3=float(message.text))
    data = await state.get_data()
    telegram_id = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
        (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], data['expenses3'], telegram_id))
    conn.commit()
    cursor.close()
    await state.clear()
    await message.answer("Категории и расходы сохранены!")




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())