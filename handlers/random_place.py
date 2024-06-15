from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import random
from math import cos, sin, sqrt, pi
import overpy
from shapely.geometry import Polygon, Point
from keyboards import main_menu, place_type_menu
from aiogram.utils.exceptions import MessageNotModified

class RandomPlace(StatesGroup):
    waiting_for_location = State()
    waiting_for_radius = State()
    choosing_place_type = State()

async def random_place(callback_query: types.CallbackQuery, state: FSMContext):
    message = await callback_query.message.edit_text("Отправьте начальную геопозицию.")
    await state.update_data(query_message_id=message.message_id, query_message_text=message.text)
    await RandomPlace.waiting_for_location.set()

async def location_received(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.LOCATION:
        await state.update_data(location=message.location)
        response_message = await message.answer("Введите радиус в метрах:")
        await state.update_data(radius_message_id=response_message.message_id)
        await state.update_data(location_message_id=message.message_id)
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
        radius_text = message.text.replace(",", ".")
        radius = float(radius_text)
        if radius <= 0:
            raise ValueError("Radius must be positive")
        await state.update_data(radius=radius)
        await message.answer("Выберите тип места:", reply_markup=place_type_menu)
        await message.delete()
        user_data = await state.get_data()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['query_message_id'])
        await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['radius_message_id'])
        await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['location_message_id'])
        await RandomPlace.choosing_place_type.set()
    except ValueError:
        await message.delete()
        data = await state.get_data()
        radius_message_id = data.get('radius_message_id')
        if radius_message_id:
            new_text = "Радиус должен быть положительным числом❗️\nВведите радиус в метрах:"
            await edit_message_text(
                message.bot,
                chat_id=message.chat.id,
                message_id=radius_message_id,
                new_text=new_text
            )

async def random_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']
    random_point = get_random_point(location.latitude, location.longitude, radius)

    await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
    await callback_query.message.answer("Что сгенерировать? 🌀", reply_markup=main_menu)
    await callback_query.message.delete()
    await state.finish()

async def green_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']
    green_areas = get_green_areas(location.latitude, location.longitude, radius)

    if green_areas:
        random_point = get_random_point_in_green_areas(green_areas)
        if random_point:
            await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
            await callback_query.message.answer("Что сгенерировать? 🌀", reply_markup=main_menu)
            await callback_query.message.delete()
            await state.finish()
        else:
            new_text = "В радиусе нет зелёных зон ❗️\nВыберите тип места:"
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
    else:
        new_text = "В радиусе нет зелёных зон ❗️\nВыберите тип места:"
        await edit_message_text(
            callback_query.bot,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            new_text=new_text,
            reply_markup=place_type_menu
        )

async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выберите опцию:", reply_markup=main_menu)
    await state.finish()

async def edit_message_text(bot, chat_id, message_id, new_text, reply_markup=None):
    try:
        await bot.edit_message_text(
            new_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup
        )
    except MessageNotModified:
        pass

def get_green_areas(lat, lon, radius):
    api = overpy.Overpass()
    r = radius / 111300  # Convert radius to degrees
    query = f"""
    [out:json];
    (
        way["natural"="wood"](around:{radius},{lat},{lon});
        way["landuse"="forest"](around:{radius},{lat},{lon});
        way["leisure"="park"](around:{radius},{lat},{lon});
        way["natural"="grassland"](around:{radius},{lat},{lon});
    );
    (._;>;);
    out body;
    """
    result = api.query(query)

    green_areas = []
    for way in result.ways:
        nodes = way.get_nodes(resolve_missing=True)
        polygon = Polygon([(node.lon, node.lat) for node in nodes])
        green_areas.append(polygon)

    return green_areas

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

def get_random_point_in_green_areas(green_areas):
    for _ in range(10):  # Попытка 10 раз
        polygon = random.choice(green_areas)
        min_x, min_y, max_x, max_y = polygon.bounds
        while True:
            random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if polygon.contains(random_point):
                return {"lat": random_point.y, "lon": random_point.x}
    return None

def register_handlers_random_place(dp: Dispatcher):
    dp.register_callback_query_handler(random_place, lambda c: c.data == 'random_place')
    dp.register_message_handler(location_received, content_types=ContentType.ANY, state=RandomPlace.waiting_for_location)
    dp.register_message_handler(radius_received, content_types=ContentType.TEXT, state=RandomPlace.waiting_for_radius)
    dp.register_callback_query_handler(random_place_type, lambda c: c.data == 'random_place_type', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(green_place_type, lambda c: c.data == 'green_place_type', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(back_to_main_menu, lambda c: c.data == 'back_to_menu', state='*')
