from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards import main_menu

async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    await message.answer("Что сгенерировать? 🌀", reply_markup=main_menu)

def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start_command, commands="start", state="*")
