from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from .settings import RED_BOT_TOKEN

bot = Bot(token=RED_BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message) -> None:
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!")


@dp.message()
async def echo(message: types.Message) -> None:
    """
    This handler accepts any message and sends it back unchanged.
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")
