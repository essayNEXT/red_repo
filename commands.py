from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_cmd(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='start of work'
        ),
        BotCommand(
            command='set',
            description='select the interface language from Favorites'
        ),
        BotCommand(
            command='list',
            description='list supported languages'
        ),
        BotCommand(
            command='help',
            description='get help (depends on the context)'
        ),
        BotCommand(
            command='add',
            description='transfer of the bot to the bot echo test mode and back'
        ),
        BotCommand(
            command='test',
            description='transfer of the bot to the bot echo test mode and back'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
