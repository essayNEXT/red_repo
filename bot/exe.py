if __name__ == "__main__":
    from aiogram import executor
    from handlers import dp

    print("BOT started!")

    executor.start_polling(dp, skip_updates=True)
