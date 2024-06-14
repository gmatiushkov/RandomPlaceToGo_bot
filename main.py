from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from handlers import start, random_place, random_station

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация хендлеров
start.register_handlers_start(dp)
random_place.register_handlers_random_place(dp)
random_station.register_handlers_random_station(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
