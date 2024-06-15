from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from handlers import start, random_place, random_station, random_direction

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация хендлеров
start.register_handlers_start(dp)
random_place.register_handlers_random_place(dp)
random_station.register_handlers_random_station(dp)
random_direction.register_handlers_random_direction(dp)

# Обработчик для удаления всех сообщений, если бот не находится в состоянии ожидания
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def delete_unexpected_messages(message: types.Message):
    await message.delete()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
