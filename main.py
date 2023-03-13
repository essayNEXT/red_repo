import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from settings import BOT_TOKEN
from handlers import router
from commands import set_cmd
import logging


async def start_bot():

    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    #dp.message.register(start_command, Command(commands=['start', 'help', 'set', 'list']))  # CommandStart()


    # формуємо меню команд
    await set_cmd(bot)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    print('Start BOT')
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
    asyncio.run(start_bot())
