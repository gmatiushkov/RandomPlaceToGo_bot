from aiogram import types, Dispatcher
from keyboards import direction_menu, main_menu
import random

async def random_direction(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите генерацию направления:", reply_markup=direction_menu)

async def generate_left_right(callback_query: types.CallbackQuery):
    direction = random.choice(["Налево ⬅️", "Направо ➡️"])
    await callback_query.message.answer(f"{direction}")
    await callback_query.message.answer("Выберите генерацию направления:", reply_markup=direction_menu)
    await callback_query.message.delete()  # Удаляем старое сообщение с меню

async def generate_all_directions(callback_query: types.CallbackQuery):
    direction = random.choice(["Прямо ⬆️", "Назад ⬇️", "Направо ➡️", "Налево ⬅️"])
    await callback_query.message.answer(f"{direction}")
    await callback_query.message.answer("Выберите генерацию направления:", reply_markup=direction_menu)
    await callback_query.message.delete()  # Удаляем старое сообщение с меню

async def back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Что сгенерировать? 🌀", reply_markup=main_menu)

def register_handlers_random_direction(dp: Dispatcher):
    dp.register_callback_query_handler(random_direction, lambda c: c.data == 'direction')
    dp.register_callback_query_handler(generate_left_right, lambda c: c.data == 'left_right')
    dp.register_callback_query_handler(generate_all_directions, lambda c: c.data == 'all_directions')
    dp.register_callback_query_handler(back_to_menu, lambda c: c.data == 'back_to_menu')
