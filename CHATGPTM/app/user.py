
from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.database.requests import set_user
from app.states import Work
from asyncio import sleep
from mistralai import Mistral
from config import AI_TOKEN
user = Router()



@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer('Добро пожаловать в бот!')

@user.message(Command("help"))
async def cmd_help(message: Message):
    await set_user(message.from_user.id)
    help_text = """
    Команды, которые поддерживает бот:

/start - начать работу с ботом

/help - получить список команд(это сообщение)

/info - получить описание доступных моделей
    """
    await message.answer(help_text, reply_markup=main_menu)

@user.message(Command("info"))
async def cmd_help(message: Message):
    await set_user(message.from_user.id)
    info_text = """
    Какие есть модели:

mistral-large-latest - Модель высшего уровня для решения сложных задач с последней версией, выпущенной в ноябре 2024 года. 

mistral-small-latest - Более слабая модель, но работает немного быстрее. Выпущена в сентябре 2024 года. 

codestral-latest - Передовая языковая модель для программирования выпущена в мае 2024 года. 
    """
    await message.answer(info_text)

@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваш запрос ещё обрабатывается!")


MAX_MESSAGE_LENGTH = 4096


async def send_long_message(message: Message, text: str):
    while len(text) > MAX_MESSAGE_LENGTH:
        await message.answer(text[:MAX_MESSAGE_LENGTH-3]+'```')
        text = '```   ' + text[MAX_MESSAGE_LENGTH-3:]
    await message.answer(text)



@user.message(lambda message: message.content_type==ContentType.TEXT)
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    processing_message = await message.answer("GPT обрабатывает ваш запрос, пожалуйста, подождите...")

    res = await generate(message.text)
    #print(res.choices[0].message.content)
    response_text = res.choices[0].message.content
    #await processing_message.edit_text(response_text)
    if len(response_text)>MAX_MESSAGE_LENGTH:
        await processing_message.edit_text("Ответ слишком длинный, отправляю по частям...")
        await send_long_message(message,response_text)
    else:
        await processing_message.edit_text(response_text)
    await state.clear()

@user.message(lambda message: message.content_type==ContentType.STICKER)
async def ai(message: Message, state: FSMContext):
    sticker_id = message.sticker.file_id
    await message.answer_sticker(sticker_id)
    await state.clear()




@user.message()
async def ai(message: Message, state: FSMContext):
    await message.answer("К сожалению, я пока умею обрабатывать только текстовые сообщения...")
    await state.clear()

model_name = "mistral-small-latest"

# Создаем кнопки основного меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выбор модели", callback_data="choose_model")],
    [InlineKeyboardButton(text="Перейти на сайт", url="https://mistral.ai/")]
])

# Создаем кнопки для выбора модели
model_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="mistral large", callback_data="mistral-large-latest")],
    [InlineKeyboardButton(text = "mistral small", callback_data="mistral-small-latest")],
    [InlineKeyboardButton(text = "codestral", callback_data="codestral-latest")],
    [InlineKeyboardButton(text = "Назад", callback_data="back_to_main")]
])

# Роутер для обработки кноп
@user.callback_query()
async def handle_callback_query(callback: CallbackQuery):
    global model_name

    # Переход к выбору модели
    if callback.data == "choose_model":
        await callback.message.edit_text("Выберите модель:", reply_markup=model_menu)

    # Возврат в главное меню
    elif callback.data == "back_to_main":
        await callback.message.edit_text("Выберите действие:", reply_markup=main_menu)

    # Выбор модели
    elif callback.data in["mistral-large-latest","mistral-small-latest","codestral-latest"]:
        model_name = callback.data  # Извлекаем номер модели
        await callback.answer(f"Вы выбрали Модель {model_name}.")
        await callback.message.edit_text(
            f"Вы выбрали Модель {model_name}. Возврат в главное меню.",
            reply_markup=main_menu)


#-----------------------------------------------------------------



async def generate(content):
    delay = 1
    retries = 10
    for i in range(retries):
        try:
            s = Mistral(
                api_key=AI_TOKEN,
            )
            res = await s.chat.complete_async(model=model_name, messages=[
                {
                    "content": content,
                    "role": "user",
                },
            ])
            if res is not None:
                return res
        except Exception as e:
            if "429" in str(e):
                await sleep(delay)
                delay+=1
