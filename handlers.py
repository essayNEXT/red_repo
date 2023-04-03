from asyncio import sleep

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text
from aiogram import Router, F

from keyboards import localization_manager
from translate import translate_message
from keyboards.kb import kb_reply, paginator_red_team, router2, kb_favor, kb_reverse, kb_add_my, kb_train
# kb_del, kb_interface, kb_add
from db import get_langs_all, get_langs_activ, get_langs_translate, get_cards, \
    set_langs_flag, set_del_lang, set_user, set_langs_all, set_user_page, set_cards

router = Router()
router.include_router(router2)  # підключаємо роутер клавіатури
WORK = True  # Команда /test переводе бота в ехо режим, WORK = False
train = tuple()
result = 0
number = 0


class ADDChoice(StatesGroup):
    choosing_first_lang = State()
    choosing_second_lang = State()
    choosing_ok = State()


async def button_translation(user_id: str, name_buttons: tuple) -> dict:
    result = {}
    for x in name_buttons:
        result.update({x: str(await localization_manager.get_localized_message(user_id, x))})
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
    elif message.text == "/set":  # ========================= SET ======================
        texts["reply to command"] = await localization_manager.get_localized_message(user_id, "set")
        pre = "set: "  # префікс для обробки callback-a
        immutable_buttons = "OK", "Cancel", "Help", "Test eng button"  # кортеж незмінних кнопок ("Скасувати"...)
        immutable_buttons = await button_translation(user_id, immutable_buttons)
        lang_interf_list = get_langs_activ(user_id)  # отримуємо з БД список мов [('uk', 1, 0, 1), ]
        lang_interf = filter(None, (map(lambda x: x[1] * x[0], lang_interf_list))).__next__() or "en"
        localization_manager.user_conf.update(
            {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас

        # отримуємо з БД  локалізований список доступних мов
        langdict = await localization_manager.get_localized_lang(lang_interf)
        langdict = langdict.copy()
        # Формуєм словник мов, які можно вибрати для інтерфейсу
        lang_interf_dict = {}
        # цикл для показу існуючей інтерфейсної мови
        for i in lang_interf_list:
            if i[1] == 1:
                lang_interf = i[0]
                # break
            lang_interf_dict.update({i[0]: langdict[i[0]]})
        # lang_interf = filter(None, (map(lambda x: x[1] * x[0], lang_interf_list))).__next__() or "en"
        await message.answer(f'Зараз мова інтерфейсу - <b>{lang_interf}</b>',
                             reply_markup=paginator_red_team(mutable_buttons=lang_interf_dict, pre=pre,
                                                             immutable_buttons=immutable_buttons))

    # Вивести список доступних мов перекладу"  # ====================== LIST ============================
    elif message.text == "/list":
        lang_interf_list = get_langs_activ(user_id)  # отримуємо з БД список мов [('uk', 1, 0, 1), ]
        lang_interf = filter(None, (map(lambda x: x[1] * x[0], lang_interf_list))).__next__()

        lang_dict = get_langs_all(lang_interf)  # отримуємо з БД словник мов {Lang_code: Lang_interface}
        LANGUES = '\n'.join([f'{key}: {value}' for key, value in lang_dict.items()])
        texts["reply to command"] = LANGUES

    elif message.text == "/test":  # Тестовий режим / режим ехо-бота ============= TEST =============
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
async def show_all_lang(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    pre = 'add: '  # префікс для обробки callback-a
    immutable_buttons = "OK", "Cancel",  # [("first_lang", "second_lang"), ("Cancel",)]  # список з кортежів незмінних кнопок ("Скасувати")
    immutable_buttons = await button_translation(user_id, immutable_buttons)
    upper_immutable_buttons = ("first_lang", "second_lang")
    upper_immutable_buttons = await button_translation(user_id, upper_immutable_buttons)
    # отримуємо список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    lang_interf = filter(None, (map(lambda x: x[1] * x[0], lst))).__next__() or "en"
    localization_manager.user_conf.update(
        {str(user_id): lang_interf})  # Зміна мови юзера в тимчасовому словнику.  Тарас
    # отримуємо з БД список доступних мов
    # LANGDICT = get_langs_all(lang_interf)
    langdict = await localization_manager.get_localized_lang(lang_interf)
    langdict = langdict.copy()
    for i in lst:
        lang = i[0]
        print(f' Favorites {lang}')
        if lang in langdict:
            langdict.pop(lang, None)  # виключаємо Обрані мови зі списку мов

    if localization_manager.user_conf.get(user_id) == "sq":
        import itertools
        langdict = dict(itertools.islice(langdict.items(), 7))
    reply_markup_link = paginator_red_team(mutable_buttons=langdict, pre=pre,
                                           upper_immutable_buttons=upper_immutable_buttons,
                                           immutable_buttons=immutable_buttons)
    await message.answer(await localization_manager.get_localized_message(user_id, "add"),
                         reply_markup=reply_markup_link)

    await state.update_data(red_state=0)
    await state.update_data(red_buttons=upper_immutable_buttons)
    await state.update_data(langdict=langdict)
    await state.update_data(reply_markup_link=reply_markup_link)
    pass


# Додавання мови в "Favorites language" =============== callback button "Add" NEW=====================

@router.callback_query(Text(startswith='add:'))
async def add_lang(callback: CallbackQuery, state: FSMContext):
    async def f_choosing_ok_or_plus(user_dat: dict, curent_state) -> str | int:
        for i_button in SET_BUTTONS:
            if not user_dat.get(i_button, None):
                return curent_state + 1
                # break
        else:  # якщо всі мови встановлені, цикл пройде до кінця, і виконається цей код
            return "choosing_ok"  # state.set_state(ADDChoice.choosing_ok)

    async def f_message_text(user_dat: dict) -> str:
        return "---".join([user_dat.get(i_button, "не вибрано") for i_button in SET_BUTTONS])

    user_id = str(callback.from_user.id)
    callbk_data = callback.data.split()[1]  # відрізаємо префікс 'add:'
    user_data = await state.get_data()  # порцию {user_data['chosen_food']}
    SET_BUTTONS: tuple = user_data.get("red_buttons", None)
    lang_list: list = list(user_data.get("langdict", {}).keys())
    print(f'callback button  "Add" IN {user_id}, {callbk_data}')
    current_state = user_data.get("red_state", None)
    if callbk_data == 'ok':
        if current_state == "choosing_ok":  # ADDChoice.choosing_ok
            # set_langs_flag(user_id, lang_code, is_active=0)  для адд
            # set_langs_flag(user_id, lang_favor_src, lang_favor_target)  для фейворіт
            set_langs_flag(user_id, user_data['first_lang'], is_active=0)
            set_langs_flag(user_id, user_data['second_lang'], is_active=0)
            set_langs_flag(user_id, user_data['first_lang'], user_data['second_lang'])
            await callback.message.edit_text(text=f'callback button "Add" IN {user_id}, {callbk_data} state OK')
            await sleep(5)
            await callback.message.edit_text(text=f" дякуємо ваш вибір збережено=> "
                                                  + "---".join(
                [user_data.get(i_button, "не вибрано") for i_button in SET_BUTTONS]),
                                             # f"{user_data['first_lang']} ---- {user_data['second_lang']} ",
                                             reply_markup=None)
            await sleep(10)
            await callback.answer(
                "дякуємо ваш вибір збережено " + "---".join(
                    [user_data.get(i_button, "не вибрано") for i_button in SET_BUTTONS]),
            )
            await callback.message.delete()
            await state.clear()

            ##
        else:  # current_state == ADDChoice.choosing_second_lang or current_state == ADDChoice.choosing_first_lang:
            await callback.message.edit_text(text=f'Ви ще не зробили вибір \n. '
                                                  f'callback button "OK" IN {user_id}, {callbk_data} state {current_state}')
            await sleep(2)
            await callback.message.edit_text(
                text=await f_message_text(user_dat=user_data[:]),
                reply_markup=user_data["reply_markup_link"])

    elif callbk_data == 'cancel':
        print(f'callback button  "cancel" IN {user_id}, {callbk_data}')
        # current_state = await state.get_state()
        await callback.message.edit_text(
            text=f'callback button "cancel" IN {user_id}, {callbk_data} state {current_state}',
            reply_markup=None)
        await sleep(2)
        await callback.answer(" вибір скасовано ")
        await callback.message.delete()
        await state.clear()
        pass
    ###################################@router.callback_query(Text(startswith='add:'), ADDChoice.choosing_first_lang)
    # elif current_state == 0:  # ADDChoice.choosing_first_lang:
    #     print(f'callback button "Add" IN {user_id}, {callbk_data} state {current_state}')
    #     await callback.message.edit_text(
    #         text=f'callback button "Add" IN {user_id}, {callbk_data} state {current_state}')
    #     # await sleep(5)
    #     if callbk_data in SET_BUTTONS:  # ["first_lang", 'second_lang']:
    #         await callback.message.edit_text(text=f'Ви ще не нічого не вибирали')
    #         await sleep(2)
    #         # await callback.message.edit_text(
    #         #     text=await f_message_text(user_dat=user_data[:]),
    #         #     # text=f"{user_data.get('first_lang', 'виберіть іншу мову')} "
    #         #     #      f" ----- "
    #         #     #      f"{user_data.get('second_lang', 'виберіть іншу мову')} ",
    #         #     reply_markup=user_data["reply_markup_link"])
    #     else:
    #         user_data[SET_BUTTONS[current_state]] = callbk_data  # await state.update_data(first_lang=callbk_data)
    #         user_data["red_state"] = await f_choosing_ok_or_plus(user_dat=user_data[:], curent_state=current_state)
    #         # if user_data.get("second_lang", None):
    #         #     await state.update_data(red_state="choosing_ok")  # state.set_state(ADDChoice.choosing_ok)
    #         # else:
    #         #     await state.update_data(red_state=1)  # state.set_state(ADDChoice.choosing_second_lang)
    #     await callback.message.edit_text(
    #         text=await f_message_text(user_dat=user_data[:]),
    #         # text=f"{callbk_data} "
    #         #      f" ---290--- "
    #         #      f"{user_data.get('second_lang', 'виберіть іншу мову')} ",
    #         reply_markup=user_data["reply_markup_link"])
    #     await state.set_data({})
    #     await state.update_data(**user_data)

    ##################################@router.callback_query(Text(startswith='add:'), ADDChoice.choosing_second_lang)
    elif current_state >= 0 and (
            callbk_data in SET_BUTTONS or callbk_data in lang_list):  # ADDChoice.choosing_second_lang: перша, друга, треття і т.д.
        print(f'callback button second "Add" IN {user_id}, {callbk_data}')
        await callback.message.edit_text(text=f'callback button second "Add" IN {user_id}, {callbk_data}')
        await sleep(2)
        if callbk_data in SET_BUTTONS:  # ["first_lang", 'second_lang']:  # якщо нажали верхні дві кнопки
            await callback.message.edit_text(text=f'зробіть повторно свій вибір')
            if user_data.get(callbk_data, None):
                del user_data[callbk_data]
                user_data["red_state"] = SET_BUTTONS.index(
                    callbk_data) if current_state == "choosing_ok" else current_state - 1
                # якщо стате не ОК, тоді -1. Якщо ОК - то міняється на позицію нажатої кнопки
                # заміна 20рядків коду умови  elif current_state == ADDChoice.choosing_ok
                # state.set_state(ADDChoice.choosing_first_lang)
            else:
                await callback.message.edit_text(text=f'Ви ще не нічого не вибирали')  # ADDChoice.choosing_first_lang
            await sleep(2)
        else:  # тут вже вибрали  мову    треба придумати алгоритм або карент_стате або перший наступний
            if user_data.get(SET_BUTTONS[current_state], None):
                user_data[SET_BUTTONS[current_state]] = callbk_data
            else:
                for i_button in SET_BUTTONS:
                    if user_data.get(i_button, None):
                        user_data[i_button] = callbk_data
                        break
                else:
                    raise  # сюди ніколи не попадає
            user_data["red_state"] = await f_choosing_ok_or_plus(user_dat=user_data[:], curent_state=current_state)
            await sleep(2)
        await callback.message.edit_text(text=await f_message_text(user_dat=user_data[:]),
                                         reply_markup=user_data["reply_markup_link"])
        await state.set_data({})
        await state.update_data(**user_data)
    ################################@router.callback_query(Text(startswith='add:'), ADDChoice.choosing_ok)
    # elif current_state == ADDChoice.choosing_ok:
    #     print(f'callback button second "Add" IN {user_id}, {callbk_data}')
    #     await callback.message.edit_text(text=f'callback choosing_ok "Add" IN {user_id}, {callbk_data}')
    #     await sleep(2)
    #     if callbk_data in SET_BUTTONS:  # ["first_lang", 'second_lang']:  # якщо нажали верхні дві кнопки
    #         await callback.message.edit_text(text=f'зробіть повторно свій вибір')
    #         if user_data.get(callbk_data, None):
    #             del user_data[callbk_data]
    #             user_data["red_state"] = SET_BUTTONS.index(callbk_data)  # current_state - 1
    #         await state.set_data({})
    #         await state.update_data(**user_data)
    #         await sleep(2)
    #         await callback.message.edit_text(text=await f_message_text(user_dat=user_data[:]),
    #                                          reply_markup=user_data["reply_markup_link"])


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
    langdict = {}
    # отримуємо з БД список доступних мов
    langdict = await localization_manager.get_localized_lang(lang_interf)
    langdict = langdict.copy()

    # Формуєм словник мов, які можно видаляти
    lang_del = {}  # lang_del = []

    # цикл для виключення існуючих src, target,  interface мов (їх видаляти не можна)
    for i in lst:
        if i[1] or i[2] or i[3]:
            continue
        else:
            lang_del.update({i[0]: langdict[i[0]]})  # lang_del.append(i[0])

    print(f' Delete language {lang_del}')

    # Src, Target and Interface language cannot be deleted. Виберіть мову, яку треба видалити з Обраних

    await message.answer(await localization_manager.get_localized_message(user_id, "delete_answer"),
                         reply_markup=paginator_red_team(mutable_buttons=lang_del, pre=pre,
                                                         immutable_buttons=immutable_buttons))
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


# =================================================== Тренування =====================================
@router.message(Text(startswith=['!']))  # (Text(startswith=['pag: ']))
async def training(message: Message):
    global train, result, number
    user_id = str(message.from_user.id)
    lst = message.text.split()
    print(f'message - {lst}')
    immut_dict = {'Завершити': 'cancel', 'Продовжити': '!:'}

    if len(lst) == 1:
        train = get_cards(user_id)  # ('en', 'umbrella', 'uk', 'парасолька')
        await message.answer(text=f"Тренування, надай переклад слова <b>{train[1]}</b>  {train[0]} > {train[2]}")
    elif lst[1] == train[3]:
        number += 1
        result += 1
        await message.answer(text=f"Переклад получен. Вімінно, +1 у карму\n" \
                                  f"Ваш результат {result} из {number}", reply_markup=kb_train(immut_dict))
    else:
        number += 1
        await message.answer(text=f"Переклад получен. Помилка. Правильно - {train[3]} \n" \
                                  f"Ваш результат {result} из {number}", reply_markup=kb_train(immut_dict))


# =================================================== Тренування CALLBACK =====================================
@router.callback_query(Text(startswith='!:'))
async def call_train(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    global train
    train = get_cards(user_id)  # ('en', 'umbrella', 'uk', 'парасолька') -  випадковий кортеж даних

    await callback.message.answer(text=f"Тренування, надай переклад слова <b>{train[1]}</b>  {train[0]} > {train[2]}")

    await callback.answer('Продовжити')
    await callback.message.edit_reply_markup(reply_markup=None)
    # await callback.message.delete()


# ======================================================== Translate ==============================
@router.message()
async def translate(message: Message):
    """The bot accepts, translates and returns the translation"""

    if WORK:
        user_id = str(message.from_user.id)
        pre = 'but: '  # префікс для обробки callback-a
        buttons = ['<>', 'cancel', 'В_картки']

        source_language_code, target_language_code = get_langs_translate(user_id)

        text = translate_message(message.text, source_language_code, target_language_code)

        await message.reply(f'{source_language_code} > {target_language_code} - <b>{text}</b>',
                            reply_markup=kb_reverse(buttons, pre, text_s=message.text, text_t=text))
    else:
        await message.reply(f'Hello, {message.from_user.first_name}!\n'
                            f'<b>{message.text}</b>')


# ================================================ Translate CALLBACK ===========================
@router.callback_query(Text(startswith='but:'))
async def message_button(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    # print(callback.data)
    reverse = callback.data.split()[1]  # відрізаємо префікс 'but:'
    txt_src = callback.data.split()[2]  # переводимій текст
    txt_target = callback.data.split()[3]  # результат перекладу

    # print(f'callback  "message_button" {user_id}, {reverse}')
    # src_lang, target_lang = ' ', ' '
    src_lang, target_lang = get_langs_translate(user_id)

    if reverse == '<>':
        set_langs_flag(user_id, target_lang, src_lang)  # зберігаємо в базу зміни (реверс) мов
        await callback.answer(f'{target_lang} > {src_lang}')
        await callback.message.answer(f'Направлення перекладу змінено на {target_lang} > {src_lang}')
    elif reverse == 'В_картки':
        set_cards(user_id, src_lang, txt_src, target_lang, txt_target)
        await callback.answer(f'Додано В картки')

    # button2 = [f'{target_lang} > {src_lang}', 'В_картки']

    elif reverse == 'cancel':
        await callback.answer('cancel')
        await callback.message.edit_reply_markup(reply_markup=None)
