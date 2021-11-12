import asyncio
import time

import aioschedule
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import *
from aiogram.utils import executor

import async_reddit as sr
import db as dbr
from config import TOKEN

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

class remove(StatesGroup):

    category_choose = State()

@dp.message_handler(commands="start", state=None)
async def cmd_start(message: types.Message):
    await message.answer(text=f'Привет! {message.from_user.full_name}\n Я бот который будет отправлять тебе смешное видео каждый день.')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
                'Animal', 
                'Fail', 
                'Satire', 
                'Vine/meme', 
                'Child/Baby', 
                'Music',  
                'Other video', 
                'TV/Movie Clip',
                'Sports',
                'Gaming',
                'Compilation',
                'Prank/challenge'
                ]
    keyboard.add(*buttons)
    await message.answer(text='Выбери категорию видео которая тебе больше всего нравиться, Можешь выбрать одну или больше категорий', reply_markup=keyboard)

@dp.message_handler(commands='help', state=None)
async def cmd_help(message: types.Message):
    await message.answer(f'Я умею отвечать на команды:\n /start - Запустить бота\n /help - Получить справку\n /remove - Удалить категорию видео')

@dp.message_handler(commands='remove', state=None)
async def cmd_remove_video(message:types.Message):
    await message.answer(text='Вы выбрали такие категории:')
    dbr.cur.execute(f"SELECT DISTINCT * FROM users WHERE chat_id='{message.chat.id}'")
    for i in dbr.cur.fetchall():
        await message.answer(text=f'{i[1]}')
    await message.answer(text='Выберете категорию видео которую хотите удалить')
    await remove.category_choose.set()

@dp.message_handler(state=remove.category_choose)
async def cmd_remove_video(message:types.Message):
    dbr.remove_category(message.chat.id, message.text)
    await message.answer(f'Вы удалили категорию {message.text}')
    await state.default_state.set()


@dp.message_handler(Text(equals=[
                'Animal', 
                'Fail', 
                'Satire', 
                'Vine/meme', 
                'Child/Baby', 
                'Music', 
                'Other video', 
                'TV/Movie Clip',
                'Sports',
                'Gaming',
                'Compilation',
                'Prank/challenge']), state=None)
async def cmd_video(message: types.Message):
    dbr.user_add(message.chat.id, message.text)
    await sr.findvideo(message.text)
    with open(str(message.text.replace('/', ' '))+'.mp4', 'rb') as video:
        await message.answer_video(video, caption=f'Держи видео из категории {message.text}')

async def sendvideos():

    list = (
        'Animal', 
        'Fail', 
        'Satire', 
        'Vine/meme', 
        'Child/Baby', 
        'Music',  
        'Other video', 
        'TV/Movie Clip',
        'Sports',
        'Gaming',
        'Compilation',
        'Prank/challenge'
    )
    for video_type_from_db in list:
        dbr.cur.execute(f"SELECT DISTINCT * FROM users WHERE video_type ='{video_type_from_db}'")
        users = dbr.cur.fetchall()
        for data in users:
            await sr.findvideo(data[1])
            print('Категория', data[1])
            print('Id  человека', data[0])
            with open(str(data[1]).replace('/', ' ')+'.mp4', 'rb') as video:
                await bot.send_video(chat_id=data[0], video=video, caption=f'Привет!\n Держи новое смешное видео из категории {data[1]}')
                time.sleep(1)
        print('Done')

async def scheduler():
    aioschedule.every().day.at("08:30").do(sendvideos)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())
    print('Start polling')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)