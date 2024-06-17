from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, MessageToDeleteNotFound
import random
from math import cos, sin, sqrt, pi
import overpy
from shapely.geometry import Polygon, Point, LineString
from keyboards import main_menu, place_type_menu

class RandomPlace(StatesGroup):
    waiting_for_location = State()
    waiting_for_radius = State()
    choosing_place_type = State()
    generating = State()  # Новое состояние для блокировки повторных запросов

async def random_place(callback_query: types.CallbackQuery, state: FSMContext):
    message = await callback_query.message.edit_text("Отправьте начальную геопозицию.")
    await state.update_data(query_message_id=message.message_id, query_message_text=message.text)
    await RandomPlace.waiting_for_location.set()

async def location_received(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.LOCATION:
        user_data = await state.get_data()
        if 'query_message_id' in user_data:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['query_message_id'])
            except MessageToDeleteNotFound:
                pass
        await state.update_data(location=message.location)
        if 'radius' in user_data:
            await message.answer("Выберите тип места:", reply_markup=place_type_menu)
            await message.delete()
            await state.update_data(location_message_id=message.message_id)
            await RandomPlace.choosing_place_type.set()
        else:
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
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['query_message_id'])
        except MessageToDeleteNotFound:
            pass
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['radius_message_id'])
        except MessageToDeleteNotFound:
            pass
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=user_data['location_message_id'])
        except MessageToDeleteNotFound:
            pass
        await RandomPlace.choosing_place_type.set()
    except ValueError:
        await message.delete()
        data = await state.get_data()
        radius_message_id = data.get('radius_message_id')
        if radius_message_id:
            new_text = "Радиус должен быть положительным числом❗️\nВведите радиус в метрах:"
            try:
                await edit_message_text(
                    message.bot,
                    chat_id=message.chat.id,
                    message_id=radius_message_id,
                    new_text=new_text
                )
            except MessageToEditNotFound:
                pass

async def handle_invalid_message(message: types.Message, state: FSMContext):
    await message.delete()

async def random_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние генерации
    await RandomPlace.generating.set()

    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']
    random_point = get_random_point(location.latitude, location.longitude, radius)

    await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
    await callback_query.message.delete()
    await callback_query.message.answer("Выберите тип места:", reply_markup=place_type_menu)

    # Возвращаемся к выбору типа места
    await RandomPlace.choosing_place_type.set()

async def green_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние генерации
    await RandomPlace.generating.set()

    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']

    if radius > 10000:
        new_text = "Для генерации зелёных мест радиус должен быть не больше 10000❗️\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass
        await RandomPlace.choosing_place_type.set()  # Возвращаемся к выбору типа места
        return

    green_areas = get_green_areas(location.latitude, location.longitude, radius)

    if green_areas:
        random_point = get_random_point_in_green_areas(green_areas)
        if random_point:
            await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
            await callback_query.message.delete()
            await callback_query.message.answer("Выберите тип места:", reply_markup=place_type_menu)
        else:
            new_text = "В радиусе нет зелёных зон❗\nВыберите тип места:"
            try:
                await edit_message_text(
                    callback_query.bot,
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    new_text=new_text,
                    reply_markup=place_type_menu
                )
            except MessageToEditNotFound:
                pass
    else:
        new_text = "В радиусе нет зелёных зон❗\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass

    # Возвращаемся к выбору типа места
    await RandomPlace.choosing_place_type.set()


def calculate_threshold_area(areas, percentage=0.05):
    areas_sorted = sorted(areas)
    index = int(len(areas_sorted) * (1 - percentage))
    if index < 0 or index >= len(areas_sorted):
        return None  # Если не удается вычислить порог
    # print(areas_sorted)
    return areas_sorted[index]

async def large_green_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    await RandomPlace.generating.set()

    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']

    if radius > 10000:
        new_text = "Для генерации больших зелёных мест радиус должен быть не больше 10000❗️\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass
        await RandomPlace.choosing_place_type.set()
        return

    green_areas = get_green_areas(location.latitude, location.longitude, radius)
    areas = [degrees_to_square_meters(area.area) for area in green_areas]

    if not areas:
        new_text = "В радиусе нет зелёных зон❗\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass
        await RandomPlace.choosing_place_type.set()
        return

    threshold_area = calculate_threshold_area(areas, percentage=0.3)
    # print(threshold_area)

    large_green_areas = [area for area in green_areas if degrees_to_square_meters(area.area) > threshold_area]

    if large_green_areas:
        random_point = get_random_point_in_green_areas(large_green_areas)
        if random_point:
            await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
            await callback_query.message.delete()
            await callback_query.message.answer("Выберите тип места:", reply_markup=place_type_menu)
        else:
            new_text = "В радиусе нет больших зелёных зон❗\nВыберите тип места:"
            try:
                await edit_message_text(
                    callback_query.bot,
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    new_text=new_text,
                    reply_markup=place_type_menu
                )
            except MessageToEditNotFound:
                pass
    else:
        new_text = "В радиусе нет больших зелёных зон❗\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass

    await RandomPlace.choosing_place_type.set()


async def water_place_type(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние генерации
    await RandomPlace.generating.set()

    user_data = await state.get_data()
    location = user_data['location']
    radius = user_data['radius']

    if radius > 10000:
        new_text = "Для генерации мест у воды радиус должен быть не больше 10000❗️\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass
        await RandomPlace.choosing_place_type.set()  # Возвращаемся к выбору типа места
        return

    water_areas = get_water_areas(location.latitude, location.longitude, radius)

    if water_areas:
        random_point = get_random_point_on_water_boundary(water_areas)
        if random_point:
            await callback_query.message.answer_location(random_point['lat'], random_point['lon'])
            await callback_query.message.delete()
            await callback_query.message.answer("Выберите тип места:", reply_markup=place_type_menu)
        else:
            new_text = "В радиусе нет воды❗\nВыберите тип места:"
            try:
                await edit_message_text(
                    callback_query.bot,
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    new_text=new_text,
                    reply_markup=place_type_menu
                )
            except MessageToEditNotFound:
                pass
    else:
        new_text = "В радиусе нет воды❗\nВыберите тип места:"
        try:
            await edit_message_text(
                callback_query.bot,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                new_text=new_text,
                reply_markup=place_type_menu
            )
        except MessageToEditNotFound:
            pass

    # Возвращаемся к выбору типа места
    await RandomPlace.choosing_place_type.set()

async def change_radius(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        await callback_query.message.delete()
    except MessageToDeleteNotFound:
        pass
    message = await callback_query.message.answer("Введите новый радиус в метрах:")
    await state.update_data(radius_message_id=message.message_id)
    await RandomPlace.waiting_for_radius.set()

async def change_location(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        await callback_query.message.delete()
    except MessageToDeleteNotFound:
        pass
    message = await callback_query.message.answer("Отправьте новую начальную геопозицию.")
    await state.update_data(query_message_id=message.message_id, query_message_text=message.text)
    await RandomPlace.waiting_for_location.set()

async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Что сгенерировать? 🌀", reply_markup=main_menu)
    await state.finish()

async def edit_message_text(bot, chat_id, message_id, new_text, reply_markup=None):
    try:
        await bot.edit_message_text(
            new_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup
        )
    except (MessageNotModified, MessageToEditNotFound):
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
        if len(nodes) >= 4:
            polygon = Polygon([(node.lon, node.lat) for node in nodes])
            green_areas.append(polygon)

    return green_areas

def degrees_to_square_meters(area_in_degrees):
    meters_per_degree = 111139  # это зависит от широты, точная константа для экватора
    area_in_square_meters = area_in_degrees * (meters_per_degree ** 2)
    return area_in_square_meters


def get_water_areas(lat, lon, radius):
    api = overpy.Overpass()
    r = radius / 111300  # Convert radius to degrees
    query = f"""
    [out:json];
    (
        way["natural"="water"](around:{radius},{lat},{lon});
        way["waterway"="riverbank"](around:{radius},{lat},{lon});
        way["water"="lake"](around:{radius},{lat},{lon});
        way["water"="pond"](around:{radius},{lat},{lon});
        way["water"="reservoir"](around:{radius},{lat},{lon});
        way["waterway"="river"](around:{radius},{lat},{lon});
        way["waterway"="stream"](around:{radius},{lat},{lon});
        way["waterway"="canal"](around:{radius},{lat},{lon});
        way["natural"="coastline"](around:{radius},{lat},{lon});
        way["natural"="bay"](around:{radius},{lat},{lon});
        way["water"="lagoon"](around:{radius},{lat},{lon});
        way["water"="oxbow"](around:{radius},{lat},{lon});
        way["waterway"="dam"](around:{radius},{lat},{lon});
        relation["natural"="water"](around:{radius},{lat},{lon});
        relation["water"="lake"](around:{radius},{lat},{lon});
        relation["water"="pond"](around:{radius},{lat},{lon});
        relation["waterway"="river"](around:{radius},{lat},{lon});
    );
    (._;>;);
    out body;
    """
    result = api.query(query)

    water_areas = []
    for way in result.ways:
        nodes = way.get_nodes(resolve_missing=True)
        if len(nodes) >= 4:
            polygon = Polygon([(node.lon, node.lat) for node in nodes])
            water_areas.append(polygon)

    return water_areas

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

def get_random_point_on_water_boundary(water_areas):
    for _ in range(10):  # Попытка 10 раз
        polygon = random.choice(water_areas)
        boundary = LineString(polygon.exterior.coords)
        random_point = boundary.interpolate(random.uniform(0, boundary.length))
        return {"lat": random_point.y, "lon": random_point.x}
    return None

def register_handlers_random_place(dp: Dispatcher):
    dp.register_callback_query_handler(random_place, lambda c: c.data == 'random_place')
    dp.register_message_handler(location_received, content_types=ContentType.ANY, state=RandomPlace.waiting_for_location)
    dp.register_message_handler(radius_received, content_types=ContentType.TEXT, state=RandomPlace.waiting_for_radius)
    dp.register_message_handler(handle_invalid_message, content_types=ContentType.ANY, state=RandomPlace.waiting_for_radius)
    dp.register_message_handler(handle_invalid_message, content_types=ContentType.ANY, state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(random_place_type, lambda c: c.data == 'random_place_type', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(green_place_type, lambda c: c.data == 'green_place_type', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(large_green_place_type, lambda c: c.data == 'large_green_place_type', state=RandomPlace.choosing_place_type)  # Новый хендлер
    dp.register_callback_query_handler(water_place_type, lambda c: c.data == 'water_place_type', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(change_radius, lambda c: c.data == 'change_radius', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(change_location, lambda c: c.data == 'change_location', state=RandomPlace.choosing_place_type)
    dp.register_callback_query_handler(back_to_main_menu, lambda c: c.data == 'back_to_menu', state='*')
