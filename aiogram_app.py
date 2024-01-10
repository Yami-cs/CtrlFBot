import asyncio
from telethon.tl.functions.messages import ImportChatInviteRequest
from aiogram import types
from config import bot_token
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_user_by_tg_id, insert_user, add_text, delete_text, update_priority, update_text, get_text
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, ParseMode
import re

bot = Bot(token=bot_token)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(types.KeyboardButton("Добавить слово"))\
    .add(types.KeyboardButton("Удалить слово"))\
    .add(types.KeyboardButton("Список слов"))

def validate_link(link):
    pattern = r'https://t.me/.*'
    if re.match(pattern, link):
        return True
    else:
        return False

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    tg_id = message.from_user.id
    if get_user_by_tg_id(tg_id) is None:
        insert_user(tg_id)
    await message.answer("Добро пожаловать в бота Ctrl+F!\nБот создан для уведомлений по ключевым словам из телеграмм каналов.\nНиже перечислены основные команды.", reply_markup=menu)

class UserAdd(StatesGroup):
    text = State()
    priority = State()
    tlink = State()

@dp.message_handler(Text("Добавить слово"))
async def add(message: types.Message):
    await message.answer("Введите ключевое слово, по которому будут определяться важные сообщения.", reply_markup=types.ReplyKeyboardRemove())
    await UserAdd.text.set()

@dp.message_handler(state=UserAdd.text)
async def answer(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)\
        .add(types.KeyboardButton("Да"))\
        .add(types.KeyboardButton("Нет"))
    await state.update_data(text = message.text)
    await message.answer("Введите имеет ли этот текст приоритет:", reply_markup=kb)
    await UserAdd.next();

@dp.message_handler(state=UserAdd.priority)
async def update_prior(message: types.Message, state: FSMContext):
    if message.text == "Да":
        await state.update_data(priority = 1)
    else:
        await state.update_data(priority = 0)
    await UserAdd.next()
    await message.answer("Введите ссылку на канал:", reply_markup=ReplyKeyboardRemove());

@dp.message_handler(state=UserAdd.tlink)
async def answer(message: types.Message, state: FSMContext):
    if validate_link(message.text):
        tg_id = message.from_user.id
        await state.update_data(tlink = message.text)
        data = await state.get_data()
        update_text(tg_id, data["text"], data["priority"], data["tlink"])
        await message.answer("Добавлено.", reply_markup=menu)
        await state.finish()
    else:
        await message.answer("Вы ввели не ссылку, введите ссылку")

class UserDelete(StatesGroup):
    text = State()

@dp.message_handler(Text("Удалить слово"))
async def delete(message: types.Message):
    user_text = get_text(message.from_user.id);
    if len(user_text) != 0:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for elem in user_text:
            kb.add(types.KeyboardButton(elem["text"]))
        await message.answer("Введите слово или номер слова, которое нужно удалить.", reply_markup=kb)
        await UserDelete.text.set()
    else:
        await message.answer("У вас пока что нет слов")

@dp.message_handler(state=UserDelete.text)
async def answer(message: types.Message, state: FSMContext):
    delete_text(message.from_user.id, message.text)
    await state.finish()
    await message.answer("Слово удалено.", reply_markup=menu);


@dp.message_handler(Text("Список слов"))
async def user_word(message: types.Message):
    chat_id = message.from_user.id
    text = []
    user_text = get_text(chat_id)
    if len(user_text) != 0:
        for elem in user_text:
            if elem["priority"]:
                text.append(f'<b>Слово:</b> {elem["text"]}\n<b>Канал:</b> {elem["tlink"]}\n<b>Приоритет:</b> С приоритетом\n')
            else:
                text.append(f'<b>Слово:</b> {elem["text"]}\n<b>Канал:</b> {elem["tlink"]}\n<b>Приоритет:</b> Без приоритета\n')
            
        await message.answer("<b><i>Ваши слова:</i></b>\n" +"\n".join(text, ), reply_markup=menu, disable_web_page_preview=True, parse_mode=ParseMode.HTML)
    else:
        await message.answer("У вас пока что нет слов")

if __name__ == "__main__":
    print("Aiogram Bot Started")
    asyncio.run(dp.start_polling())