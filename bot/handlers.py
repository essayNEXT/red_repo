from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from settings import BOT_TOKEN
from aiogram import Bot, Dispatcher
from translate import translate_message


bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help", "info"])
async def start_command(message: Message):
    """Bot raises this handler if '/start', '/help' or '/info' command is chosen"""
    user_name = message.from_user.first_name
    chat_id = message.from_user.id
    texts = {"reply to command": ""}

    if message.text == "/start":
        texts["reply to command"] = f"Привіт, {user_name}!\nВведіть слово для перекладу:"

    elif message.text == "/help":
        texts["reply to command"] = "Для того щоб розпочати вивчення мови - просто пишіть мені слова, " \
                                    "словосполучення чи речення, які ви хочете перекласти.\n" \
                                    "Я відразу дам Вам відповідь!"

    elif message.text == "/info":
        texts["reply to command"] = "Я допоможу Вам вивчити англійську мову!\n" \
                                    "Все дуже просто - напишіть мені щось і я перекладу :)"

    reply = texts["reply to command"]
    await bot.send_message(text=reply, chat_id=chat_id)


@dp.message_handler()
async def translate(message: Message):
    """The bot accepts, translates and returns the translation"""
    text = translate_message(message.text)
    await message.answer(text)
    
    
    
    
