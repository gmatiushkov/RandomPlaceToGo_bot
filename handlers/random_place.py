from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified
import random
from math import cos, sin, sqrt, pi
from keyboards import main_menu

class RandomPlace(StatesGroup):
    waiting_for_location = State()
    waiting_for_radius = State()

async def random_place(callback_query: types.CallbackQuery, state: FSMContext):
    message = await callback_query.message.answer("Отправьте начальную геопозицию.")
    await state.update_data(query_message_id=message.message_id, query_message_text=message.text)
    await RandomPlace.waiting_for_location.set()

async def location_received(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.LOCATION:
        await state.update_data(location=message.location)
        response_message = await message.answer("Введите радиус в метрах:")
        await state.update_data(query_message_id=response_message.message_id, query_message_text=response_message.text)
        await RandomPlace.waiting_for_radius.set()
    else:
        await message.delete()
        data = await state.get_data()
        query_message_id = data.get('query_message_id')
        query_message_text = data.get('query_message_text')
        if query_message_id:
            new_text = "Отправьте геопозицию❗️\nОтправьте начальную геопозицию."
            if query_message_text != new_text:
                await edit_message_text(
                    message.bot,
                    chat_id=message.chat.id,
                    message_id=query_message_id,
                    new_text=new_text
                )
                await state.update_data(query_message_text=new_text)

async def radius_received(message: types.Message, state: FSMContext):
    try:
        radius = float(message.text)
        if radius <= 0:
            raise ValueError("Radius must be positive")
        user_data = await state.get_data()
        location = user_data['location']
        random_point = get_random_point(location.latitude, location.longitude, radius)
        await message.answer_location(random_point['lat'], random_point['lon'])
        await state.finish()
        await message.answer("Выберите опцию:", reply_markup=main_menu)
    except ValueError:
        await message.delete()
        data = await state.get_data()
        query_message_id = data.get('query_message_id')
        query_message_text = data.get('query_message_text')
        if query_message_id:
            new_text = "Радиус должен быть положительным числом❗️\nВведите радиус в метрах:"
            if query_message_text != new_text:
                await edit_message_text(
                    message.bot,
                    chat_id=message.chat.id,
                    message_id=query_message_id,
                    new_text=new_text
                )
                await state.update_data(query_message_text=new_text)

async def edit_message_text(bot, chat_id, message_id, new_text):
    try:
        await bot.edit_message_text(
            new_text,
            chat_id=chat_id,
            message_id=message_id
        )
    except MessageNotModified:
        pass

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
