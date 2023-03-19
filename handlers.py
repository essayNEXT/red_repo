from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text
from aiogram import Router, F
from kb import keyboard, kb_add, router2, kb_favor, kb_del, kb_interface

from settings import project_id
from lang_target import get_supported_languages
from translate import translate_message
import sqlite3
import asyncio


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
    lang_code = message.from_user.language_code

    user_id_str = str(user_id)
    texts = {"reply to command": ""}

    if message.text == "/start":
        texts["reply to command"] = f"Привіт, <b>{user_name}</b>.\n " \
                                f"By default, the Telegram interface language is set.\n" \
                                f"English is also installed. \n\n" \
                                f"Click 'Add' to add the language to Favorites,\n" \
                                f"Click 'Favorites' to choose the direction of translation\n\n" \
                                f"Command /set - allows you to set the interface language from your favorites.\n" \
                                f"If you don't have the language you want, add it to Favorites first"
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
        # проверка регистрации пользователя
        if myresult is None or myresult == [] or myresult == ():
            mycursor = con.cursor()
            sql = "INSERT INTO users (telegram_id, lang_code, interface_lang, target_lang, src_lang) VALUES (?, ?, ?, ?, ?)"
            val = (user_id_str, lang_code, 1, 1, 0)
            mycursor.execute(sql, val)

            # если lang_code != 'en' додаємо англ, як src_lang
            if lang_code != 'en':
                val = (user_id_str, 'en', 0, 0, 1)
                mycursor.execute(sql, val)
            con.commit()
            await message.reply("Registered")
        else:
            await message.reply("You have already register in bot")

            #получаем от гугла список поддерживаемых языков на языке пользователя
        LANGDICT = get_supported_languages(project_id, lang_code)

            # записываем справочник от гугла в БД
        mycursor.execute("Delete from languages")  # обнуляем базу
        sql = "INSERT INTO languages (lang_code, lang_name) VALUES (?, ?)"
        for key, value in LANGDICT.items():
            val = (key, value)
            mycursor.execute(sql, val)

        con.commit()

    elif message.text == "/help":
        texts["reply to command"] = "Для того щоб розпочати вивчення мови - просто пишіть мені слова, " \
                                    "словосполучення чи речення, які ви хочете перекласти.\n" \
                                    "Я відразу дам Вам відповідь!\n" \

    elif message.text == "/set":
        texts["reply to command"] = 'Тут треба вибрати мову інтерфейсу з доступних Обраних\n' \
                                    'Якщо потрібної мови немає, додайте спочатку її до Favorites'

        # Відобразити обрані мови - команда "/set"

        mycursor = con.cursor()
        sql = "SELECT lang_code, interface_lang FROM users WHERE telegram_id = ? and is_active=1"
        adr = (user_id,)
        mycursor.execute(sql, adr)
        lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',0), ('bg',0), ('uk',1), ('en',0)]

        lang_interf_dict = dict(lst)
        lang_interf = ''
        # цикл для показу існуючей інтерфейсної мови
        for i, j in lang_interf_dict.items():
            if j == 1:
                lang_interf = i

        await message.answer(f'now interface language - <b>{lang_interf}</b>, you can change it',
                             reply_markup=kb_interface(lang_interf_dict))

    # Вивести список доступних мов перекладу"
    elif message.text == "/list":
        mycursor = con.cursor()
        sql = "SELECT lang_code, lang_name FROM languages"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()   # отримуємо список кортежів
        # print(myresult)
        LANGDICT = dict(myresult)
        LANGUES = '\n'.join([f'{key}: {value}' for key, value in LANGDICT.items()])
        texts["reply to command"] = LANGUES

    reply = texts["reply to command"]

    # викликаємо ReplyKeyboard (Выбор, добавление, удаление языка)
    await message.answer(text=reply, reply_markup=keyboard)


# Відобразити обрані мови (напрямок перекладу) - кнопка "Favorites" ==========================
@router.message(F.text == 'Favorites')
async def show_favor_lang(message: Message):

    user_id = str(message.from_user.id)
    mycursor = con.cursor()
    sql = "SELECT lang_code, src_lang, target_lang FROM users WHERE telegram_id = ? and is_active=1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('uk', 0, 1), ('en', 1, 0)]

    # active direction translation
    lang_favor = []
    lang_favor_src = ''
    lang_favor_target = ''
    for i in lst:
        if i[1]:
            lang_favor_src = i[0]
        if i[2]:
            lang_favor_target = i[0]
        lang_favor.append(i[0])

    await message.answer(f'active direction translation  <b>{lang_favor_src} > {lang_favor_target}</b>, you can change it',
                         reply_markup=kb_favor(lang_favor))


# Додати в Обрані мови (відобразити всі мови) - кнопка "Add" ======================================
@router.message(F.text == 'Add')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)

    # отримуємо список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    mycursor = con.cursor()
    sql = "SELECT lang_code FROM users WHERE telegram_id = ? and is_active = 1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('ru',), ('bg',), ('uk',), ('en',)]

    # отримуємо з БД список доступних мов
    sql = "SELECT lang_code, lang_name FROM languages"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()  # отримуємо список кортежів
    # print(myresult)
    LANGDICT = dict(myresult)

    for i in lst:  # LANGDICT.keys():
        lang = i[0]
        print(f' Favorites {lang}')
        if lang in LANGDICT:
            LANGDICT.pop(lang)
    import itertools
    LANGDICT = dict(itertools.islice(LANGDICT.items(), 7))
    await message.answer('Select language', reply_markup=kb_add(LANGDICT))


# видалити мову з обраних - кнопка "Delete"
@router.message(F.text == 'Delete')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)
    mycursor = con.cursor()
    sql = "SELECT lang_code, interface_lang, target_lang, src_lang FROM users WHERE telegram_id = ? and is_active = 1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('uk', 1, 0, 1), ('en', 0, 1, 0)]

    # Формуєм список мов, які можно видаляти
    lang_del = []

    # цикл для виключення існуючих src, target,  interface мов (їх видаляти не можна)
    for i in lst:
        if i[1] or i[2] or i[3]:
            continue
        else:
            lang_del.append(i[0])
    print(f' Delete language {lang_del}')
    # Src, Target and Interface language cannot be deleted. Виберіть мову, яку треба видалити з Обраних
    await message.answer('Select the language you want to remove from Favorites',
                         reply_markup=kb_del(lang_del))


#=======================================================================================
# Select interface language (callback command /set)
# Прочитати з БД дані в словник, потім занести в БД словник з новими даними {lang_code: interface_lang}
@router.callback_query(Text(startswith=['set:']))  # F.data.startswith('set:')  вход - "set: {i}"
async def call_select_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_interf = callback.data.split()[1]  # відрізаємо префікс 'set:'
    print(f'callback Interface input - {user_id} {lang_interf}')

    # считуємо з БД список Вибраних мов
    mycursor = con.cursor()
    sql = "SELECT lang_code, interface_lang FROM users WHERE telegram_id = ? and is_active=1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('uk', 1), ('en', 0)]
    print(f'Read DB > Interface {lst}')

    # змінюємо список згідно нових обраних мов та записуємо нові дані в БД
    for i in lst:
        if i[0] == lang_interf:
            interface_lang = 1
        else:
            interface_lang = 0
        print(f'Interface_lang > DB {i[0]}, {interface_lang}')

        sql = "UPDATE users SET interface_lang = ? WHERE telegram_id = ? and lang_code = ?"  # VALUES (?)
        val = (interface_lang, user_id, i[0])
        mycursor.execute(sql, val)

    # обновить список доступных языков на новом интерфейсном языке
    # получаем от гугла список поддерживаемых языков на языке пользователя
    LANGDICT = get_supported_languages(project_id, lang_interf)

    # записываем справочник от гугла в БД
    mycursor.execute("Delete from languages")  # обнуляем базу
    sql = "INSERT INTO languages (lang_code, lang_name) VALUES (?, ?)"
    for key, value in LANGDICT.items():
        val = (key, value)
        mycursor.execute(sql, val)
    # print(LANGDICT)
    con.commit()

    await callback.answer(lang_interf)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# ========================================================================================
# Select target  language (callback button "Favorites" )
# Прочитати з БД дані в словник, потім занести в БД словник з новими даними {lang_code: target_lang}
@router.callback_query(Text(startswith=['fav:']))  # F.data.startswith('set:')  вход - "fav: {i},{j}"
async def call_select_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_favor = callback.data.split()[1]  # відрізаємо префікс 'fav:'
    lang_favor_src = lang_favor.split(',')[0]
    lang_favor_target = lang_favor.split(',')[1]
    print(f'callback Favorites input - {user_id} {lang_favor_src} > {lang_favor_target}')

    # считуємо з БД список Вибраних мов
    mycursor = con.cursor()
    # if pre == 'set:':
    #     sql = "SELECT lang_code, interface_lang FROM users WHERE telegram_id = ? and is_active=1"
    # else:
    sql = "SELECT lang_code, src_lang, target_lang FROM users WHERE telegram_id = ? and is_active=1"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('uk', 0, 1), ('en', 1, 0)]
    print(f'DB > Favorites {lst}')

    # змінюємо список згідно нових обраних мов та записуємо нові дані в БД

    for i in lst:
        src_lang = '0'
        target_lang = '0'
        if lang_favor_src == i[0]:
            src_lang = '1'
        elif lang_favor_target == i[0]:
            target_lang = '1'

        print(f' Favorites > DB {i[0]}, {src_lang}, {target_lang}')
        sql = "UPDATE users SET src_lang = ?, target_lang = ? WHERE telegram_id = ? and lang_code = ?"  # VALUES (?)
        val = (src_lang, target_lang, user_id, i[0])
        mycursor.execute(sql, val)
    con.commit()

    await callback.answer(lang_favor)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# кнопка Cancel Inline клавіатур
@router.callback_query(Text(text='cancel'))
async def cancel(callback: CallbackQuery):
    await callback.answer(callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Додавання мови в "Favorites language" (callback button "Add") ==================================
@router.callback_query(Text(startswith='add:'))  # lambda query: query.data in lang_list)
async def add_lang(callback: CallbackQuery):

    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]   # відрізаємо префікс 'add:'
    print(f'callback button "Add" IN {user_id}, {lang_code}')

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
    print(f'callback button "Add" lst_active_0 {lst_active0}')

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
    print(f'callback button "Delete" IN {user_id}, {lang_code}')

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

    sql = "SELECT lang_code, src_lang, target_lang " \
          "FROM users " \
          "WHERE telegram_id = ? and " \
          "(src_lang=1 or target_lang=1)"
        # "SELECT lang_code FROM users WHERE telegram_id=? and target_lang = 1"
    adr = (user_id_str,)
    mycursor.execute(sql, adr)
    result = mycursor.fetchall()  # отримуємо список кортежів [('uk', 0, 1), ('en', 1, 0)]
    print(f' translate input - {result}')

    source_language_code = ''
    target_language_code = ''
    for r in result:
        if r[1] == 1:
            source_language_code = r[0]
        if r[2] == 1:
            target_language_code = r[0]

    print(f' translate out - {source_language_code} > {target_language_code}')

    text = translate_message(message.text, source_language_code, target_language_code)
    await message.answer(text)


# async def delete_message(message: Message, sleep_time: int = 0):
#     await asyncio.sleep(sleep_time)
#
#     await message.delete()