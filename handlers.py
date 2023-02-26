from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from settings import BOT_TOKEN, LANGDICT, DEFAULT_LANG_CODE, LANGUES
from aiogram import Bot, Dispatcher
from translate import translate_message
from kb import keyboard, keyboard_in, keyboard_all, kb


bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)
target_language_code = DEFAULT_LANG_CODE


@dp.message_handler(commands=["start", "help", "info", "list"])
async def start_command(message: Message):
    """Bot raises this handler if '/start', '/help', '/info' or '/list' command is chosen"""
    user_name = message.from_user.first_name
    texts = {"reply to command": ""}

    if message.text == "/start":
        texts["reply to command"] = f"Привіт, {user_name}!\nВведіть слово для перекладу:"

    elif message.text == "/help":
        texts["reply to command"] = "Для того щоб розпочати вивчення мови - просто пишіть мені слова, " \
                                    "словосполучення чи речення, які ви хочете перекласти.\n" \
                                    "Я відразу дам Вам відповідь!\n" \
                                    "/list - Вивести список доступних мов перекладу"
    elif message.text == "/info":
        texts["reply to command"] = "Я допоможу Вам вивчити англійську мову!\n" \
                                    "Все дуже просто - напишіть мені щось і я перекладу :)"
    elif message.text == "/list":
        texts["reply to command"] = LANGUES  # виводимо список мов

    reply = texts["reply to command"]
    # викликаємо клавіатуру з пропозицією обрати мову перекладу
    await message.answer(text=reply, reply_markup=keyboard)


# відображаємо Inline клавіатуру з вибором мови
@dp.message_handler(Text(equals=['Favorites language']))
async def show_favorites(message: Message):
    await message.answer('Favorites language', reply_markup=keyboard_in)


# відображаємо клавіатуру з всіма мовами
@dp.message_handler(Text(equals=['All language']))
async def show_all_lang(message: Message):
    await message.answer('All language', reply_markup=kb)  # keyboard_all - InlineKeyboard


# опис кнопок Інлайн клавіатури
@dp.callback_query_handler(text_contains='en')
async def en_kb(call: CallbackQuery):
    global target_language_code
    target_language_code = 'en'
    await call.answer('en')
    await call.message.edit_reply_markup(reply_markup=None)


@dp.callback_query_handler(text_contains='uk')
async def uk_kb(call: CallbackQuery):
    global target_language_code
    target_language_code = 'uk'
    await call.answer('uk')
    await call.message.edit_reply_markup(reply_markup=None)


@dp.callback_query_handler(text_contains='ru')
async def ru_kb(call: CallbackQuery):
    global target_language_code
    target_language_code = 'ru'
    await call.answer('ru')
    await call.message.edit_reply_markup(reply_markup=None)


@dp.callback_query_handler(text_contains='cancel')
async def cancel(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=None)


@dp.message_handler()
async def translate(message: Message):
    """The bot accepts, translates and returns the translation"""
    text = translate_message(message.text, target_language_code)
    await message.answer(text)
