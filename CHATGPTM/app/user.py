
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.database.requests import set_user
from app.generators import generate
from app.states import Work

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
    await message.answer(help_text)

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
        text = '```' + text[MAX_MESSAGE_LENGTH-3:]
    await message.answer(text)



@user.message()
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