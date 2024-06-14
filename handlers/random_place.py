from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import random
from math import cos, sin, sqrt, pi
from keyboards import main_menu

class RandomPlace(StatesGroup):
    waiting_for_location = State()
    waiting_for_radius = State()

async def random_place(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Пожалуйста, отправьте начальную геопозицию.")
    await RandomPlace.waiting_for_location.set()

async def location_received(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.LOCATION:
        await state.update_data(location=message.location)
        await message.answer("Введите радиус в метрах:")
        await RandomPlace.waiting_for_radius.set()
    else:
        await message.delete()
        await message.answer("Пожалуйста, отправьте геопозицию.")

async def radius_received(message: types.Message, state: FSMContext):
    try:
        radius = float(message.text)
        user_data = await state.get_data()
        location = user_data['location']
        random_point = get_random_point(location.latitude, location.longitude, radius)
        await message.answer_location(random_point['lat'], random_point['lon'])
        await state.finish()
        await message.answer("Выберите опцию:", reply_markup=main_menu)
    except ValueError:
        await message.delete()
        await message.answer("Пожалуйста, введите числовое значение радиуса.")

def get_random_point(lat, lon, radius):
    r = radius / 111300  # Convert radius to degrees
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    w = r * sqrt(u)
    t = 2 * pi * v
    x = w * cos(t)
    y = w * sin(t)
    new_lat = lat + x
    new_lon = lon + y
    return {"lat": new_lat, "lon": new_lon}

def register_handlers_random_place(dp: Dispatcher):
    dp.register_callback_query_handler(random_place, lambda c: c.data == 'random_place')
    dp.register_message_handler(location_received, content_types=ContentType.ANY, state=RandomPlace.waiting_for_location)
    dp.register_message_handler(radius_received, content_types=ContentType.TEXT, state=RandomPlace.waiting_for_radius)
