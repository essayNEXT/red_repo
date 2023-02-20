from main import dp, bot
from aiogram.dispatcher.filters import Text
from aiogram.types import Message


@dp.message_handler(Text)
async def echo(message: Message):
    chat_id = message.from_user.id
    text = f"You said: {message.text}"
    await bot.send_message(text=text, chat_id=chat_id)
