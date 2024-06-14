import random
import logging
from math import cos, sin, pi
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from geopy.distance import geodesic

# Установите токен вашего бота здесь
API_TOKEN = '5824768991:AAEqW0JNmIljg8rwI1I8j5PwljWqOEPoOFo'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    location = State()
    radius = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне геопозицию и выбери радиус для генерации случайной точки.")
    await Form.location.set()

@dp.message_handler(content_types=['location'], state=Form.location)
async def handle_location(message: types.Message, state: FSMContext):
    location = message.location
    async with state.proxy() as data:
        data['location'] = location
    await Form.next()
    await message.reply("Теперь выбери радиус в километрах (например, 5).")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.radius)
async def process_radius_invalid(message: types.Message):
    return await message.reply("Пожалуйста, введите правильное число для радиуса.")

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.radius)
async def handle_radius(message: types.Message, state: FSMContext):
    radius = float(message.text)
    async with state.proxy() as data:
        location = data['location']
    random_point = generate_random_point(location.latitude, location.longitude, radius)
    await bot.send_location(message.chat.id, random_point.latitude, random_point.longitude)
    await state.finish()

def generate_random_point(lat, lon, radius_km):
    radius_m = radius_km * 1000
    u = random.random()
    v = random.random()
    w = radius_m * (u ** 0.5)
    t = 2 * pi * v
    x = w * cos(t)
    y = w * sin(t)

    # Используем геодезические вычисления для получения новой точки
    destination = geodesic(meters=w).destination((lat, lon), t)
    return destination

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
