from aiogram import executor
from handlers import dp


if __name__ == '__main__':
    print("BOT started!")
    executor.start_polling(dp, skip_updates=True)
