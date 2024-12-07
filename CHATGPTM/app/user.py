from aiogram import Router, F, types, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from app.database.requests import set_user
# from middlewares import BaseMiddleware
from app.generators import generate
from app.states import Work
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user = Router()

# user.message.middleware(BaseMiddleware())

@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "Модель 1", callback_data="button1"),
        ],
        [
            InlineKeyboardButton(text = "Модель 2", callback_data="button2"),
        ],
        [
            InlineKeyboardButton(text = "Модель 3", callback_data="button3"),
        ]
    ])

    await message.answer('Добро пожаловать в бот!', reply_markup=keyboard)

@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваш запрос ещё обрабатывается!")

@user.message()
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    processing_message = await message.answer("GPT обрабатывает ваш запрос, пожалуйста, подождите...")
    res = await generate(message.text)
    await sleep(1)
    #print(res.choices[0].message.content)
    response_text = res.choices[0].message.content
    await processing_message.edit_text(response_text)
    await state.clear()
