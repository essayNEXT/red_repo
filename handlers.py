from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text
from aiogram import Router, F
from kb import keyboard, kb_add, router2, kb_favor, kb_del
from settings import LANGDICT, LANGUES, lang_list
from translate import translate_message
import sqlite3

# для початку роботи треба запустити Create_sqlite.py і створити БД SQLite
try:
    con = sqlite3.connect('.venv/bot.sqlite3')  # підключення до БД
    print("База даних успішно підключена")
except sqlite3.Error as error:
    print("Помилка при підключенні до БД", error)

    ''' Опис полів БД
        telegram_id - id користувача (беремо з телеграма за командою /start)
        lang_code - код мови, яку додаємо до Вибраних
        interface_lang - мова інтерфейсу, одна з Вибраних
        target_lang - вказує на поточну цільову мову перекладу (якою перекладаємо)
        is_active - видаляє мову з Вибраних, якщо interface_lang=0 і target_lang=0
    '''

router = Router()
router.include_router(router2)  # подключаем роутер клавиатуры


@router.message(Command(commands=['start', 'help', 'set', 'list']))
async def start_command(message: Message):
    """Bot raises this handler if '/start', '/help', '/set' or '/list' command is chosen"""

    user_name = message.from_user.first_name
    # user_last_name = message.from_user.last_name
    user_id = message.from_user.id
    user_lang = message.from_user.language_code

    user_id_str = str(user_id)
    texts = {"reply to command": ""}

    if message.text == "/start":
        texts["reply to command"] = f"Привіт, <b>{user_name}</b>.\n " \
                                    f"By default, only the Telegram interface language is set.\n" \
                                    f"Click 'Add' to add the target language to Favorites."
                                   # f'За замовчуванням встановлена мова інтерфейсу - українська'
                                   # f"<tg-spoiler>{user_last_name}, " \
                                   # f"{user_id} " \
                                   # f"{user_lang}!</tg-spoiler>\nВведіть слово для перекладу:"

        # реєстрація користувача в БД
        mycursor = con.cursor()  # створюємо об'єкт курсор (для виконання операцій з БД)
        sql = "SELECT * FROM users WHERE telegram_id = ?"
        adr = (user_id_str,)
        mycursor.execute(sql, adr)
        myresult = mycursor.fetchall()
        print(myresult)

        if myresult is None or myresult == [] or myresult == ():
            mycursor = con.cursor()
            sql = "INSERT INTO users (telegram_id, lang_code, interface_lang, target_lang) VALUES (?, ?, ?, ?)"
            val = (user_id_str, user_lang, 1, 1)
            mycursor.execute(sql, val)
            con.commit()
            await message.reply("Registered")
        else:
            await message.reply("You have already register in bot")

    elif message.text == "/help":
        texts["reply to command"] = "Для того щоб розпочати вивчення мови - просто пишіть мені слова, " \
                                    "словосполучення чи речення, які ви хочете перекласти.\n" \
                                    "Я відразу дам Вам відповідь!\n" \

    elif message.text == "/set":
        texts["reply to command"] = 'Тут треба вибрати мову інтерфейсу з доступних Обраних'

        # Відобразити обрані мови - команда "/set"

        mycursor = con.cursor()
        sql = "SELECT lang_code, interface_lang FROM users WHERE telegram_id = ? and is_active=1"
        adr = (user_id,)
        mycursor.execute(sql, adr)
        lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',0), ('bg',0), ('uk',1), ('en',0)]
        lst.append(('00', 'set'))  # mix in the flag that defines the command /set
        lang_favor_dict = dict(lst)
        lang_favor = ''
        # цикл для показу існуючей інтерфейсної мови
        for i, j in lang_favor_dict.items():
            if j == 1:
                lang_favor = i

        await message.answer(f'now interface language - <b>{lang_favor}</b>, you can change it',
                             reply_markup=kb_favor(lang_favor_dict))

    elif message.text == "/list":
        texts["reply to command"] = LANGUES  # Вивести список доступних мов перекладу"

    reply = texts["reply to command"]

    # викликаємо ReplyKeyboard (Выбор, добавление, удаление языка)
    await message.answer(text=reply, reply_markup=keyboard)


# Відобразити обрані мови - кнопка "Favorites"
@router.message(F.text == 'Favorites')
async def show_favor_lang(message: Message):

    user_id = str(message.from_user.id)
    mycursor = con.cursor()
    sql = "SELECT lang_code, target_lang FROM users WHERE telegram_id = ? and is_active=1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',0), ('bg',0), ('uk',1), ('en',0)]
    lst.append(('01', 'fav'))  # mix in the flag that determines the button click Favorites
    lang_favor_dict = dict(lst)
    lang_favor = ''
    # цикл для показу існуючей целевой мови переркладу
    for i, j in lang_favor_dict.items():
        if j == 1:
            lang_favor = i

    await message.answer(f'now target language - <b>{lang_favor}</b>, you can change it',
                         reply_markup=kb_favor(lang_favor_dict))


# Додати в Обрані мови (відобразити всі мови) - кнопка "Add"
@router.message(F.text == 'Add')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)

    # отримуємо список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    mycursor = con.cursor()
    sql = "SELECT lang_code FROM users WHERE telegram_id = ? and is_active = 1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',), ('bg',), ('uk',), ('en',)]

    for i in lst:  # LANGDICT.keys():
        lang = i[0]
        print(lang)
        if lang in LANGDICT:
            LANGDICT.pop(lang)

    await message.answer('Select language', reply_markup=kb_add(LANGDICT))


# видалити мову з обраних - кнопка "Delete"
@router.message(F.text == 'Delete')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)
    mycursor = con.cursor()
    sql = "SELECT lang_code, interface_lang, target_lang FROM users WHERE telegram_id = ? and is_active = 1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru', 0, 0), ('bg', 0, 0), ('uk', 1, 0), ('en', 0, 1)]

    # Формуєм список мов, які можно видаляти
    lang_del = []

    # цикл для виключення існуючей целевой мови та мови ынтерфейсу (видалити не можно)
    for i in lst:
        if i[1] or i[2]:
            continue
        else:
            lang_del.append(i[0])
    print(lang_del)
    # Target or Interface language cannot be deleted Виберіть мову, яку треба видалити з Обраних
    await message.answer('Select the language you want to remove from Favorites',
                         reply_markup=kb_del(lang_del))


# Select target (interface) language (callback button "Favorites" and command /set)
# Прочитати з БД дані в словник, потім занести в БД словник з новими даними {lang_code: target_lang}
@router.callback_query(Text(startswith=['set:', 'fav:']))  # F.text.startswith('set:')
async def call_select_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    pre = callback.data.split()[0]  # отримуємо префікс
    lang_code = callback.data.split()[1]  # відрізаємо префікс 'set:' or 'fav:'
    print(user_id, lang_code)

    # считуємо з БД список Вибраних мов
    mycursor = con.cursor()
    if pre == 'set:':
        sql = "SELECT lang_code, interface_lang FROM users WHERE telegram_id = ? and is_active=1"
    else:
        sql = "SELECT lang_code, target_lang FROM users WHERE telegram_id = ? and is_active=1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',0), ('bg',0), ('uk',1), ('en',0)]
    lang_favor_dict = dict(lst)

    # змінюємо словник згідно нової вибраної мови та записуємо нові дані в БД
    for i, j in lang_favor_dict.items():
        if lang_code == i:
            j = 1
        else:
            j = 0
        print(i, j)
        if pre == 'set:':
            sql = "UPDATE users SET interface_lang = ? WHERE telegram_id = ? and lang_code = ?"  # VALUES (?)
        else:
            sql = "UPDATE users SET target_lang = ? WHERE telegram_id = ? and lang_code = ?"  # VALUES (?)
        val = (j, user_id, i)
        mycursor.execute(sql, val)
    con.commit()

    await callback.answer(callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# кнопка Cancel Inline клавіатур
@router.callback_query(Text(text='cancel'))
async def cancel(callback: CallbackQuery):
    await callback.answer(callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Додавання мови в "Favorites language" (callback button "Add")
@router.callback_query(Text(startswith='add:'))  # lambda query: query.data in lang_list)
async def add_lang(callback: CallbackQuery):

    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]   # відрізаємо префікс 'add:'
    print(user_id, lang_code)

    # Зчитати з БД список мов з прапором is_active=0
    mycursor = con.cursor()
    sql = "SELECT lang_code FROM users WHERE telegram_id = ? and is_active=0"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',), ('bg',), ('uk',), ('en',)]

    # якщо мова для додавання входить в считаний список, просто підняти прапор (is_active=1)
    lst_active0 = []
    for i in lst:
        lst_active0.append(i[0])  # список ['ru', 'bg', 'uk', 'en']
    print(lst_active0)

    if lang_code in lst_active0:
        sql = "UPDATE users SET is_active = ? WHERE telegram_id = ? and lang_code = ?"
        val = (1, user_id, lang_code)
        mycursor.execute(sql, val)

    # якщо мова для додавання не входить в считаний список мов з is_active=0, додади мову в БД
    else:
        sql = "INSERT INTO users (telegram_id, lang_code) VALUES (?, ?)"
        val = (user_id, lang_code)
        mycursor.execute(sql, val)

    con.commit()
    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Видалення мови з Обраних (callback button "Delete")
@router.callback_query(Text(startswith='del:'))  # lambda query: query.data in lang_list)
async def add_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]   # відрізаємо префікс 'del:'
    print(user_id, lang_code)

    # Встановлюемо флаг is_active = 0 для мови, яку треба видалити
    mycursor = con.cursor()
    sql = "UPDATE users SET is_active = ? WHERE telegram_id = ? and lang_code = ?"
    val = (0, user_id, lang_code)
    mycursor.execute(sql, val)
    con.commit()

    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Translate not the latest version function translate_message
# planning to connect source language
@router.message()
async def translate(message: Message):
    """The bot accepts, translates and returns the translation"""
    user_id_str = str(message.from_user.id)
    mycursor = con.cursor()
    sql = "SELECT lang_code FROM users WHERE telegram_id=? and target_lang = 1"
    adr = (user_id_str,)
    mycursor.execute(sql, adr)
    result = mycursor.fetchone()  # отримуємо кортеж(lang_code, )
    target_language_code = result[0]  # отримуємо  #lang_code
    print(target_language_code)

    text = translate_message(message.text, target_language_code)
    await message.answer(text)
