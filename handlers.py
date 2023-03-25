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
from keyboards.kb import kb_reply, kb_add, router2, kb_favor, kb_del, kb_interface, kb_reverse
from db import get_langs_all,  get_langs_activ, get_langs_translate, \
                set_langs_flag, set_del_lang, set_user, set_langs_all


router = Router()
router.include_router(router2)  # підключаємо роутер клавіатури
WORK = True  # Команда /test переводе бота в ехо режим, WORK = False


@router.message(Command(commands=['start', 'help', 'set', 'list', 'test']))
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
        # f'За замовчуванням встановлена мова інтерфейсу - українська'
        # f"<tg-spoiler>{user_last_name}, " \
        # f"{user_id} " \
        # f"{user_lang}!</tg-spoiler>\nВведіть слово для перекладу:"

        # реєстрація користувача в БД
        set_user(user_id, lang_code)
        # отримуємо від гугла словник підтримуваних мов мовою користувача, записуємо його у БД
        set_langs_all(lang_code)

    elif message.text == "/help": # ========================= HELP ======================
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "help")
    
    # Відобразити обрані мови - команда "/set"
    elif message.text == "/set":   # ========================= SET ======================
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "set")
        pre = "set: " 			        # префікс для обробки callback-a
        immutable_buttons = "Cancel",   # кортеж незмінних кнопок ("Скасувати"...)

        lang_interf_list = get_langs_activ(user_id)  # отримуємо з БД список мов [('uk', 1, 0, 1), ]
        lang_interf = ''
        # цикл для показу існуючей інтерфейсної мови
        for i in lang_interf_list:
            if i[1] == 1:
                lang_interf = i[0]
                break
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

    reply = texts["reply to command"]
    await message.answer(text=reply, reply_markup=reply_markup)


# ================Відобразити обрані мови (напрямок перекладу) ============== Favorites =============
@router.message(F.text == 'Favorites')
async def show_favor_lang(message: Message):
    pre = 'fav: '  # префікс для обробки callback-a
    immutable_buttons = "Cancel",   # кортеж незмінних кнопок ("Скасувати")
    user_id = str(message.from_user.id)
    
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

    await message.answer(f'active direction translation  <b>{lang_favor_src} > {lang_favor_target}</b>,\n'
                         'you can change it',
                         reply_markup=kb_favor(lang_favor, pre, immutable_buttons, lst_len=len(lang_favor)-1))


# Додати в Обрані мови (відобразити всі мови) - кнопка "Add" ============== ADD Paginator Taras ===============
@router.message(F.text == 'Add')
async def show_all_lang(message: Message):
    pre = 'add: '  # префікс для обробки callback-a
    immutable_buttons = "Cancel",   # кортеж незмінних кнопок ("Скасувати")
    user_id = str(message.from_user.id)

    # отримуємо список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]

    # отримуємо з БД список доступних мов
    LANGDICT = get_langs_all()

    for i in lst:  
        lang = i[0]
        print(f' Favorites {lang}')
        if lang in LANGDICT:
            LANGDICT.pop(lang)  # виключаємо Обрані мови зі списку мов
            
    if localization_manager.user_conf.get(user_id) == "sq":
        import itertools
        LANGDICT = dict(itertools.islice(LANGDICT.items(), 7))
    await message.answer(await localization_manager.get_localized_message(user_id, "add"),
                         reply_markup=kb_add(LANGDICT, pre, immutable_buttons))


# видалити мову з обраних - кнопка "Delete"  ======================== DELETE ===============================
@router.message(F.text == 'Delete')
async def show_all_lang(message: Message):
    pre = 'del: '  # префікс для обробки callback-a
    immutable_buttons = "Cancel",  # кортеж незмінних кнопок ("Скасувати")
    user_id = str(message.from_user.id)
    
    # отримуємо з БД список обраних мов 
    lst = get_langs_activ(user_id) # отримуємо список кортежів [('uk', 1, 0, 1), ]

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


#========================================== CALLBACKS =================== SET ======================
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
    lang_code = callback.data.split()[1]   # відрізаємо префікс 'add:'
    print(f'callback button "Add" IN {user_id}, {lang_code}')

    set_langs_flag(user_id, lang_code, is_active=0)
    
    await callback.answer(lang_code)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()


# Видалення мови з Обраних ======================== callback button "Delete") =====================
@router.callback_query(Text(startswith='del:'))  
async def add_lang(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    lang_code = callback.data.split()[1]   # відрізаємо префікс 'del:'
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

    if reverse == '<>':
        src_lang, target_lang = get_langs_translate(user_id)
        set_langs_flag(user_id, target_lang, src_lang)   # зберігаємо в базу зміни (реверс) мов
    elif reverse == 'В_картки':
        pass

    await callback.answer(f'{target_lang} > {src_lang}')
    button2 = [f'{target_lang} > {src_lang}', 'В_картки']
    await callback.message.answer(f'Направлення перекладу змінено на {target_lang} > {src_lang}')
    

