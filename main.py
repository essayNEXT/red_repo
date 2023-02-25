from aiogram import executor
from handlers import dp
from settings import DEFAULT_LANG_CODE

if __name__ == '__main__':
    print(f"BOT started! Default Language = {DEFAULT_LANG_CODE}")
    executor.start_polling(dp, skip_updates=True)
