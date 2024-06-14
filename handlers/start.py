from aiogram import types, Dispatcher
from keyboards import main_menu

async def start_command(message: types.Message):
    await message.answer("Что сгенерировать? 🌀", reply_markup=main_menu)

def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start_command, commands="start")
