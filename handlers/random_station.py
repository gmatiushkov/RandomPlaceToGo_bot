from aiogram import types, Dispatcher
from keyboards import metro_menu, main_menu
import random

metro_stations = {
    "🟥": ["Девяткино", "Гражданский проспект", "Академическая", "Политехническая", "Площадь Мужества", "Лесная",
          "Выборгская", "Площадь Ленина", "Чернышевская", "Площадь Восстания", "Владимирская", "Пушкинская",
          "Технологический институт", "Балтийская", "Нарвская", "Кировский завод", "Автово", "Ленинский проспект",
          "Проспект Ветеранов"],
    "🟦": ["Парнас", "Проспект Просвещения", "Озерки", "Удельная", "Пионерская", "Чёрная речка", "Петроградская",
          "Горьковская", "Невский проспект", "Сенная площадь", "Технологический институт", "Фрунзенская",
          "Московские ворота", "Электросила", "Парк Победы", "Московская", "Звёздная", "Купчино"],
    "🟩": ["Беговая", "Новокрестовская", "Приморская", "Василеостровская", "Гостиный двор", "Маяковская",
          "Площадь Александра Невского 1", "Елизаровская", "Ломоносовская", "Пролетарская", "Обухово", "Рыбацкое"],
    "🟧": ["Спасская", "Достоевская", "Лиговский проспект", "Площадь Александра Невского 2", "Новочеркасская",
          "Ладожская", "Проспект Большевиков", "Улица Дыбенко"],
    "🟪": ["Комендантский проспект", "Старая Деревня", "Крестовский остров", "Чкаловская", "Спортивная",
          "Адмиралтейская", "Садовая", "Звенигородская", "Обводный канал", "Волковская", "Бухарестская",
          "Международная", "Проспект Славы", "Дунайская", "Шушары"],
}

all_stations = [(station, color) for color, stations in metro_stations.items() for station in stations]

async def random_station(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите ветку метро:", reply_markup=metro_menu)

async def station_selected(callback_query: types.CallbackQuery):
    color = callback_query.data.split('_')[1]
    if color == "all":
        station, station_color = random.choice(all_stations)
    else:
        station = random.choice(metro_stations[color])
        station_color = color

    await callback_query.message.edit_text(f"{station} {station_color}")
    await callback_query.message.answer("Выберите ветку метро:", reply_markup=metro_menu)

async def back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Что сгенерировать? 🌀", reply_markup=main_menu)

def register_handlers_random_station(dp: Dispatcher):
    dp.register_callback_query_handler(random_station, lambda c: c.data == 'random_station')
    dp.register_callback_query_handler(station_selected, lambda c: c.data.startswith('metro_'))
    dp.register_callback_query_handler(back_to_menu, lambda c: c.data == 'back_to_menu')
