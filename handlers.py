from typing import Tuple, List

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text
from aiogram import Router, F

# from kb import keyboard, kb_add, router2, kb_favor, kb_del, kb_interface
# from settings import project_id
# from lang_target import get_supported_languages
# from kb import kb_reply, kb_add, router2, kb_favor, kb_del, kb_interface

from keyboards import localization_manager
from translate import translate_message
from keyboards.kb import kb_reply, kb_add, router2, kb_favor, kb_del, kb_interface, kb_reverse, kb_add_my
from db import get_langs_all, get_langs_activ, get_langs_translate, \
    set_langs_flag, set_del_lang, set_user, set_langs_all, set_user_page

router = Router()
router.include_router(router2)  # підключаємо роутер клавіатури
WORK = True  # Команда /test переводе бота в ехо режим, WORK = False

async def button_translation(user_id: str, name_buttons: tuple) -> dict:
    result = {}
    for x in name_buttons:
        result.update({x:str(await localization_manager.get_localized_message(user_id, x))})
    return result

@router.message(Command(commands=['start', 'help', 'set', 'list', 'add', 'test']))
async def start_command(message: Message):
    """Bot raises this handler if '/start', '/help', '/set', '/list' or /test command is chosen"""

    user_name = message.from_user.first_name
    # user_last_name = message.from_user.last_name
    # username = message.from_user.username  # 'Ihor_master'
    user_id = str(message.from_user.id)
    lang_code = message.from_user.language_code

    texts = {"reply to command": ""}
    kb_list = ['Favorites', 'Add', 'Delete']  # викликаємо ReplyKeyboard (Вибір, додавання, видалення мови) ===
    reply_markup = kb_reply(kb_list)

    if message.text == "/start":  # ========================= START ======================
        # заношу код мови у свій словничок, бо нема часу розбратися з БД. Тарас
        # user_conf = {} file = localization.py
        await localization_manager.get_user_language(user_id, lang_code)
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "hello", user_name)

        # реєстрація користувача в БД
        set_user(user_id, lang_code)
        # отримуємо від гугла словник підтримуваних мов мовою користувача, записуємо його у БД
        set_langs_all(lang_code)

    elif message.text == "/help":  # ========================= HELP ======================
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "help")

    # Відобразити обрані мови - команда "/set"
    elif message.text == "/set":   # ========================= SET ======================
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "set")
        pre = "set: "  # префікс для обробки callback-a
        immutable_buttons = "OK", "Cancel", "Help", "Test eng button"  # кортеж незмінних кнопок ("Скасувати"...)
        immutable_buttons = await button_translation(user_id, immutable_buttons)
        lang_interf_list = get_langs_activ(user_id)  # отримуємо з БД список мов [('uk', 1, 0, 1), ]
        lang_interf = "en"
        # цикл для показу існуючей інтерфейсної мови
        for i in lang_interf_list:
            if i[1] == 1:
                lang_interf = i[0]
                break
        # lang_interf = filter(None, (map(lambda x: x[1] * x[0], lang_interf_list))).__next__() or "en"
        await message.answer(f'Зараз мова інтерфейсу - <b>{lang_interf}</b>',
                             reply_markup=kb_interface(lang_interf_list, pre, immutable_buttons))

    # Вивести список доступних мов перекладу"  # ====================== LIST ============================
    elif message.text == "/list":
        LANGDICT = get_langs_all()  # отримуємо з БД словник мов {Lang_code: Lang_interface}
        LANGUES = '\n'.join([f'{key}: {value}' for key, value in LANGDICT.items()])
        texts["reply to command"] = LANGUES

    elif message.text == "/test":  # Тестовий режим / режим ехо-бота ============== TEST =============
        global WORK
        if WORK:
            WORK = False
            texts["reply to command"] = '<b>Бот переведен в тестовий режим ехо-бота</b>'
            reply_markup = None
        else:
            WORK = True
            texts["reply to command"] = '<b>Бот переведен в робочий режим</b>'
            reply_markup = kb_reply(kb_list)

    elif message.text == "/add":  # ========================= ADD-NEW ==============================
        # user_id = str(message.from_user.id)
        await message.answer(text="Зроби свій вибір!", reply_markup=kb_add_my(user_id))

        texts["reply to command"] = 'Тут треба обрати мову, яку Ви хочете додати до Обраних'
    # =============================================
    reply = texts["reply to command"]
    await message.answer(text=reply, reply_markup=reply_markup)

# ==============================================CALLBACK ADD-NEW =================================
@router.callback_query(Text(startswith=['next: ']))
async def call_test_next(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    page = int(callback.data.split()[1])  # отримуємо номер сторінки, що відображається
    page += 1
    set_user_page(user_id, page)
    await callback.answer(page)
    await callback.message.edit_reply_markup(reply_markup=kb_add_my(user_id, page))


@router.callback_query(Text(startswith=['prev: ']))
async def call_test_prev(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    page = int(callback.data.split()[1])  # отримуємо номер сторінки, що відображається
    page -= 1
    set_user_page(user_id, page)
    await callback.answer(page)
    await callback.message.edit_reply_markup(reply_markup=kb_add_my(user_id, page))


@router.callback_query(Text(startswith=['pag: ']))
async def call_test_pag(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]  # отримуємо номер сторінки, що відображається

    print(f'IN callback "Add-NEW"  {user_id}, {lang_code}')
    set_langs_flag(user_id, lang_code, is_active=0)

    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# ================Відобразити обрані мови (напрямок перекладу) ============== Favorites =============
@router.message(F.text == 'Favorites')
async def show_favor_lang(message: Message):
    user_id = str(message.from_user.id)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    lang_interf = filter(None, (map(lambda x: x[1] * x[0], lst))).__next__() or "en"
    localization_manager.user_conf.update(
        {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас
    pre = 'fav: '  # префікс для обробки callback-a
    immutable_buttons = "OK", "Cancel",  # кортеж незмінних кнопок ("Скасувати")
    immutable_buttons = await button_translation(user_id, immutable_buttons)

    # отримуємо з БД список кортежів [('uk', 1, 0, 1), ] [lang_code, interface_lang, src_lang, target_lang]
    lst = get_langs_activ(user_id)

    # active direction translation
    lang_favor = []
    lang_favor_src = ''
    lang_favor_target = ''
    for i in lst:  # determine active direction translation
        if i[2]:
            lang_favor_src = i[0]
        if i[3]:
            lang_favor_target = i[0]
        lang_favor.append(i[0])

    # lang_favor = list(map(lambda x: x[0], lst))
    # lang_favor_src = list(filter(None, (map(lambda x: x[2] * x[0], lst))))[0]
    # lang_favor_target= list(filter(None, (map(lambda x: x[3] * x[0], lst))))[0]

    await message.answer(await localization_manager.get_localized_message(user_id, "favorites_answer",
                                                                          lang_favor_src, lang_favor_target),
                         reply_markup=kb_favor(lang_favor, pre, immutable_buttons, lst_len=len(lang_favor) - 1))


# Додати в Обрані мови (відобразити всі мови) - кнопка "Add" ============== ADD Paginator Taras ===============
@router.message(F.text == 'Add')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)
    pre = 'add: '  # префікс для обробки callback-a
    immutable_buttons = "Cancel",  # кортеж незмінних кнопок ("Скасувати")
    immutable_buttons = await button_translation(user_id, immutable_buttons)

    # отримуємо список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    lang_interf = filter(None, (map(lambda x: x[1] * x[0], lst))).__next__() or "en"
    localization_manager.user_conf.update(
        {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас
    # отримуємо з БД список доступних мов
    # LANGDICT = get_langs_all()
    langdict = await localization_manager.get_localized_lang(lang_interf)
    for i in lst:
        lang = i[0]
        print(f' Favorites {lang}')
        if lang in langdict:
            langdict.pop(lang, None)  # виключаємо Обрані мови зі списку мов

    if localization_manager.user_conf.get(user_id) == "sq":
        import itertools
        langdict = dict(itertools.islice(langdict.items(), 7))
    await message.answer(await localization_manager.get_localized_message(user_id, "add"),
                         reply_markup=kb_add(langdict, pre, immutable_buttons))


# видалити мову з обраних - кнопка "Delete"  ======================== DELETE ===============================
@router.message(F.text == 'Delete')
async def show_all_lang(message: Message):
    user_id = str(message.from_user.id)
    # отримуємо з БД список обраних мов
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    lang_interf = filter(None, (map(lambda x: x[1] * x[0], lst))).__next__() or "en"
    localization_manager.user_conf.update(
        {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас
    pre = 'del: '  # префікс для обробки callback-a
    immutable_buttons = "Cancel",  # кортеж незмінних кнопок ("Скасувати")
    immutable_buttons = await button_translation(user_id, immutable_buttons)



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

    await message.answer(await localization_manager.get_localized_message(user_id, "delete_answer"),
                         reply_markup=kb_del(lang_del, pre, immutable_buttons))
    # await message.answer('Select the language you want to remove from Favorites',
    #                      reply_markup=kb_del(lang_del, pre, immutable_buttons))


# ========================================== CALLBACKS =================== SET ======================
# Select interface language (callback command /set)
# Прочитати з БД дані, потім занести в БД нові дани

@router.callback_query(Text(startswith=['set:']))  # F.data.startswith('set:')  вход - "set: {i}"
async def call_select_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_interf = callback.data.split()[1]  # відрізаємо префікс 'set:'

    print(f'input callback Interface  - {user_id} {lang_interf}')
    localization_manager.user_conf.update(
        {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас

    # зберігаємо в базу зміни мови інтерфейсу
    set_langs_flag(user_id, lang_interf)

    # отримуємо від гугла новий список підтримуваних мов новою мовою користувача
    set_langs_all(lang_interf)

    await callback.answer(lang_interf)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# ================================================== CALLBACK Favorites =======================
# Select target  language (callback button "Favorites" )
# Прочитати з БД дані, потім занести в БД нові дани

@router.callback_query(Text(startswith=['fav:']))  # F.data.startswith('set:')  вход - "fav: {i}>{j}"
async def call_select_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_favor = callback.data.split()[1]  # відрізаємо префікс 'fav:'
    lang_favor_src, lang_favor_target = lang_favor.split('>')

    print(f'input callback Favorites  - {user_id} {lang_favor_src} > {lang_favor_target}')

    # зберігаємо в базу зміни src, target мов
    set_langs_flag(user_id, lang_favor_src, lang_favor_target)

    await callback.answer(lang_favor)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# ========================================== кнопка Cancel Inline клавіатур ==================
@router.callback_query(Text(text='cancel'))
async def cancel(callback: CallbackQuery):
    await callback.answer(callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Додавання мови в "Favorites language" =============== callback button "Add" =====================
@router.callback_query(Text(startswith='add:'))
async def add_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]  # відрізаємо префікс 'add:'
    print(f'callback button "Add" IN {user_id}, {lang_code}')

    set_langs_flag(user_id, lang_code, is_active=0)

    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Видалення мови з Обраних ======================== callback button "Delete") =====================
@router.callback_query(Text(startswith='del:'))
async def add_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]  # відрізаємо префікс 'del:'
    print(f'callback button "Delete" IN {user_id}, {lang_code}')

    # зберігаємо в базу зміни мов
    set_del_lang(user_id, lang_code)

    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# ======================================================== Translate ==============================
@router.message()
async def translate(message: Message):
    """The bot accepts, translates and returns the translation"""

    if WORK:
        user_id = str(message.from_user.id)
        pre = 'but: '  # префікс для обробки callback-a
        buttons = ['<>', 'В_картки']

        source_language_code, target_language_code = get_langs_translate(user_id)

        text = translate_message(message.text, source_language_code, target_language_code)

        await message.reply(f'{source_language_code} > {target_language_code} - <b>{text}</b>',
                            reply_markup=kb_reverse(buttons, pre))
    else:
        await message.reply(f'Hello, {message.from_user.first_name}!\n'
                            f'<b>{message.text}</b>')


# ================================================ Translate CALLBACK ===========================
@router.callback_query(Text(startswith='but:'))
async def message_button(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    reverse = callback.data.split()[1]  # відрізаємо префікс 'but:'

    print(f'callback  "message_button" {user_id}, {reverse}')
    src_lang, target_lang = ' ', ' ' \
                                 ''
    if reverse == '<>':
        src_lang, target_lang = get_langs_translate(user_id)
        set_langs_flag(user_id, target_lang, src_lang)  # зберігаємо в базу зміни (реверс) мов
    elif reverse == 'В_картки':
        pass

    await callback.answer(f'{target_lang} > {src_lang}')
    button2 = [f'{target_lang} > {src_lang}', 'В_картки']
    await callback.message.answer(f'Направлення перекладу змінено на {target_lang} > {src_lang}')
