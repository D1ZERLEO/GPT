from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from app.database.requests import set_user
from app.generators import generate
from app.states import Work

user = Router()

#переменная имени модели
model_name = None


@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)

    #клавиатура
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Модель 1")],
            [KeyboardButton(text="Модель 2")],
            [KeyboardButton(text="Модель 3")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await message.answer('Добро пожаловать в бот! Выберите модель:', reply_markup=keyboard)


@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваш запрос ещё обрабатывается!")


@user.message(lambda message: message.text in ["Модель 1", "Модель 2", "Модель 3"])
async def select_model(message: Message, state: FSMContext):
    global model_name
    model_name = message.text  # Сохраняем выбранную модель

    await message.answer(f'Вы выбрали {model_name}. Теперь введите ваш запрос.')
    await state.set_state(Work.process)


@user.message(Work.process)
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)

    if model_name is None:
        await message.answer("Сначала выберите модель.")
        return

    processing_message = await message.answer("GPT обрабатывает ваш запрос, пожалуйста, подождите...")

    # Используем model_name для генерации ответа
    res = await generate(message.text, model = model_name)  # Передаем model_name в функцию generate
    await sleep(1)

    response_text = res.choices[0].message.content
    await processing_message.edit_text(response_text)
    await state.clear()
