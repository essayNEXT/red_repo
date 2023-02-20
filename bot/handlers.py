from main import dp, bot
from aiogram.dispatcher.filters import Text
from aiogram.types import Message


@dp.message_handler(commands=["start", "help", "info"])
async def start_command(message: Message):
    """Bot raises this handler if '/start', '/help' or '/info' command is chosen"""
    user_name = message.from_user.first_name
    chat_id = message.from_user.id
    texts = {"text": ""}

    if message.text == "/start":
        texts["text"] = f"Привіт, {user_name}!\nВведіть слово для перекладу:"

    elif message.text == "/help":
        texts["text"] = "Для того щоб розпочати вивчення мови - просто пишіть мені слова, словосполучення чи " \
                        "речення, які ви хочете перекласти.\nЯ відразу дам Вам відповідь!"

    elif message.text == "/info":
        texts["text"] = "Я допоможу Вам вивчити англійську мову!\nВсе дуже просто - напишіть мені щось і я перекладу :)"

    reply = texts["text"]
    await bot.send_message(text=reply, chat_id=chat_id)


@dp.message_handler(Text)
async def echo(message: Message):
    """Simple echo handler. Need to convert this handler into translation handler"""
    chat_id = message.from_user.id
    text = f"You said: {message.text}"
    await bot.send_message(text=text, chat_id=chat_id)
