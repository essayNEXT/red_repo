from typing import Dict, Iterable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, Dispatcher
from keyboards.paginator_taras import Paginator
from db import get_langs_all, get_langs_activ, get_user_page

router2 = Router()


# викликаємо ReplyKeyboard (Вибір, додавання, видалення мови) - new
def kb_reply(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Створює реплай-клавіатуру із кнопками в один ряд
    :param items: список текстів для кнопок
    :return: об'єкт реплай-клавіатури
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True, one_time_keyboard=True)


# ============================== KeyboardPaginatorRedTeam(Paginator) =======================
class KeyboardPaginatorRedTeam(Paginator):
    """
    Доповнення основного класу-пагінатора можливістю додавати знизу незмінних/постійних(immutable) клавіш
    Службовий/внутрішній клас до функції paginator_red_team
    """

    def __init__(self, immutable_buttons=None, upper_immutable_buttons=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.immutable_buttons = immutable_buttons
        self.upper_immutable_buttons = upper_immutable_buttons

    def __call__(self, *args, **kwargs):
        paginator = super().__call__(*args, **kwargs)
        paginator.inline_keyboard.insert(0, self.upper_immutable_buttons) if self.upper_immutable_buttons else None
        paginator.inline_keyboard.append(self.immutable_buttons) if self.immutable_buttons else None
        return paginator


def paginator_red_team(mutable_keyboard: types.InlineKeyboardMarkup |
                                         Iterable[types.InlineKeyboardButton] |
                                         Iterable[Iterable[types.InlineKeyboardButton]] |
                                         InlineKeyboardBuilder = None,
                       mutable_buttons: Dict = None,
                       pre: str = None,
                       column: int = 3,
                       row: int = 5,
                       upper_immutable_buttons: Dict = None,
                       immutable_buttons: Dict = None,
                       dp: Router = router2,
                       *args, **kwargs):
    """
    Обробка кнопок Inline- клавіатури, з можливість пагінації "основної" частини.

    Обов'язкові параметри - mutable_keyboard або mutable_buttons та pre

    Функція обробляє клавіші двох видів, схематично розділені на "змінні"(mutable) та "незмінні"(immutable).
    На виході оброблені дані передаються в клас-обробник KeyboardPaginatorRedTeam, для кінцевого формування клавіатури
        заданої конфігурації та властивостей пагінації.

    Вхідні параметри для "змінних"(mutable) можуть бути надані через:
            - mutable_keyboard - набір готових ТГ об'єктів: кнопок/клавіатур
            - mutable_buttons - простий словник з набором реквізитів(текст на кнопці та друга частинка
                    для ідентифікації callback_data) а також pre - перша половина callback_data

    Вхідні параметри для "незмінної"(immutable) чистини клавіатури - це простий словник з набором реквізитів(текст
            на кнопці та дані для ідентифікації callback_data)

    На вхід приймає клавіші основної частини, які можуть змінні клавіші
    :param mutable_keyboard: набір готових ТГ об'єктів, для формування основної частини Inline-клавіатури користувача
                  types.InlineKeyboardMarkup |
                  Iterable[types.InlineKeyboardButton] |
                  Iterable[Iterable[types.InlineKeyboardButton]] |
                  InlineKeyboardBuilder
    :param mutable_buttons: Dict[sts: str] словник з набором параметрів, для формування основної частини Inline-клавіатури користувача
    :param pre: перша половина callback_data
    :param upper_immutable_buttons: словник з набором параметрів, для формування верхньої частини Inline-клавіатури незмінних кнопок
    :param immutable_buttons: словник з набором параметрів, для формування нижньої частини Inline-клавіатури незмінних кнопок
    :param dp:
    :param column: кількість кнопок в ряді
    :param row:  кількість рядів на одному листі пагінації
    :param args:  додаткові параметри
    :param kwargs:
    :return: повертає готовий ТГ-об'єкт Inline-клавіатуру для інтерактивної комунікації користувача з програмою
    """
    if upper_immutable_buttons:  # формування незмінних кнопок upper клави
        upper_immutable_buttons = [InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk.lower()}')
                             for callbk, text in upper_immutable_buttons.items()]
    if immutable_buttons:  # формування незмінних кнопок знизу клави
        immutable_buttons = [InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk.lower()}')
                             for callbk, text in immutable_buttons.items()]
    else:
        immutable_buttons = types.InlineKeyboardButton(text='Cancel', callback_data='cancel')

    if mutable_buttons and pre:  # формування змінних кнопок клави
        mutable_keyboard = InlineKeyboardBuilder()
        for callbk, text in mutable_buttons.items():
            mutable_keyboard.add(InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk}'))

    mutable_keyboard.adjust(column)
    paginator = KeyboardPaginatorRedTeam(data=mutable_keyboard, upper_immutable_buttons=upper_immutable_buttons,
                                         immutable_buttons=immutable_buttons, size=row, dp=dp)
    # paginator = Paginator(data=mutable_keyboard.as_markup(), size=row, dp=dp)
    return paginator()


# ============================== InlineKeyboard ADD Paginator Taras =========================
# def kb_add(lang_dict, pre: str, immutable_buttons: dict[str], column=3, row=5):
#     """
#        Створює inline-клавіатуру Add languages (додавання мови в Обрані)
#        :param
#        lang_dict: словник текстів для кнопок
#             {Lang_code: Lang_name}
#        pre: префікс для обробки callback-a
#        immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)
#
#        :option column=3, row=5 - число колонок і строк відображення кнопок
#             вказані значення по замовчанню
#        :return: об'єкт inline-клавіатури
#        """
#     kb = InlineKeyboardBuilder()
#
#     for i, j in lang_dict.items():
#         kb.add(InlineKeyboardButton(text=j, callback_data=f'{pre} {i}'))
#     # from itertools import islice
#     # list(iter(lambda: tuple(islice((iter(kb.as_markup().inline_keyboard)), 8)), ()))
#     # kb.adjust(column)
#     # paginator = Paginator(data=kb.as_markup(), size=row, dp=router2)
#     # return paginator()
#     return paginator_red_team(mutable_keyboard=kb, immutable_buttons=immutable_buttons, dp=router2)


# ============================== Select interface language /set ===========================
# def kb_interface(lang_interface: list, pre: str, immutable_buttons: dict[str]) -> InlineKeyboardMarkup:
#     """
#        Створює inline-клавіатуру зміни мови інтерфейсу,
#        :param
#        lang_interface: список текстів для кнопок [('uk', 1, 0, 1), ('en', 0, 1, 0), (sq, 0, 0, 0)]
#        pre: префікс для обробки callback-a,
#        immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)
#
#        :return: об'єкт inline-клавіатури
#        """
#     print(f'InlineKeyboard Interface input - {lang_interface}')
#     kb = InlineKeyboardBuilder()
#
#     for i in lang_interface:  # динамичні кнопки
#         kb.add(InlineKeyboardButton(text=i[0], callback_data=f"{pre} {i[0]}"))
#
#     # незмінні кнопки      callback_data=i.lower() - що при перекладі?
#     # kb.row(*[InlineKeyboardButton(text=i, callback_data=i.lower()) for i in immutable_buttons])
#     # immutable_buttons = [InlineKeyboardButton(text=i, callback_data=i.lower()) for i in immutable_buttons]
#     # return kb.as_markup()
#     return paginator_red_team(mutable_keyboard=kb, immutable_buttons=immutable_buttons, dp=router2)


# ================================== InlineKeyboard Favorites language ===================
def kb_favor(lang_favor: list[str], pre: str, immutable_buttons: dict[str], lst_len: int) -> InlineKeyboardMarkup:
    """
      Створює inline-клавіатуру Обраних мов
      Бажано до 6 мов (щоб мови не перемішувалися),
      одна source-мова - один ряд)

      :param
      lang_favor: список текстів для кнопок
      pre: префікс для обробки callback-a
      immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)
      lst_len: кількість мов у ряду

      :return: об'єкт inline-клавіатури
    """

    print(f'InlineKeyboard Favorites input - {lang_favor}')
    kb = InlineKeyboardBuilder()
    for i in lang_favor:
        for j in lang_favor:
            if i != j:
                kb.add(InlineKeyboardButton(text=f'{i} > {j}', callback_data=f"{pre} {i}>{j}"))
                # kb.adjust(lst_len)  # Бажано до 6 Обраних мов, не більше 6 стовпчиків

    # for i in immutable_buttons:  # незмінні кнопки
    #     kb.row(InlineKeyboardButton(text=i, callback_data=i.lower()))
    # return kb.as_markup()
    return paginator_red_team(mutable_keyboard=kb, immutable_buttons=immutable_buttons, dp=router2)


# ================================== InlineKeyboard Delete language ======================
# def kb_del(lang_del: list[str], pre: str, immutable_buttons: dict[str]) -> InlineKeyboardMarkup:
#     """
#       Створює inline-клавіатуру видалення мови з Обраних
#
#       :param
#       lang_del: список текстів для кнопок
#       pre: префікс для обробки callback-a
#       immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)
#
#       :return: об'єкт inline-клавіатури
#     """
#
#     kb = InlineKeyboardBuilder()
#     for i in lang_del:
#         kb.add(InlineKeyboardButton(text=i, callback_data=f'{pre} {i}'))
#
#     # for i in immutable_buttons:  # незмінні кнопки
#     #     kb.row(InlineKeyboardButton(text=i, callback_data=i.lower()))
#     # return kb.as_markup()
#     return paginator_red_team(mutable_keyboard=kb, immutable_buttons=immutable_buttons, dp=router2)


# ================================== reverse translate ======================
def kb_reverse(buttons: list[str], pre: str, text_s:str, text_t: str, column=6) -> InlineKeyboardMarkup:
    """
    - зміна направлення перекладу на протилежне
    - додавання слова в картки для тренування
    :param buttons: список с найменуваннями кнопок
    :param pre: префікс для обробки callback-a
    :param column: максимальна кількість кнопок у рядку
    :return: об'єкт inline-клавіатури
    """
    print(buttons)
    kb = InlineKeyboardBuilder()
    for i in buttons:
        kb.add(InlineKeyboardButton(text=i, callback_data=f'{pre} {i} {text_s} {text_t}'))
    kb.adjust(column)
    return kb.as_markup()


# ========================================= ADD NEW ==============================
def kb_add_my(user_id, page=0, row=5, column=3) -> InlineKeyboardMarkup:
    """
    Альтернативна фунція додавання мови в Обрані. Зберігається стан клавіатури в БД.
    Наступний старт відбувається зі стану попередньго запуску.
    Нині підтримує однозначний вибір
    Додана можливість додавання верхніх незмінних кнопок lang_1, lang_2
    :param user_id: telegram_id користувача
    :param page: стартова сторінка
    :param row:  число строк
    :param column: число стовпчиків
    :return: об'єкт InlineKeyboardMarkup
    """
    # перевіряєм чи існує запис в табл. page
    myresult = get_user_page(user_id)
    if myresult:
        page = myresult[0]

    # отримуємо з БД список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    print(f' in Favorites {lst}')

    lang_code = filter(None, (map(lambda x: x[1] * x[0], lst))).__next__()  # отримуємо мову інтерфейсу
    print(f'lang_code = {lang_code}')

    # отримуємо з БД словник доступних мов на мові інтерфейсу
    lang_dict = get_langs_all(lang_code)


    for i in lst:
        lang = i[0]
        # print(f' Favorites {lang}')
        if lang in lang_dict:
            lang_dict.pop(lang)  # виключаємо Обрані мови зі списку мов
    lang_lst = list(lang_dict.items())

    # Розділіть список мов lang_lst на менші частини
    number_page = int(len(lang_lst) / (column * row))
    lang_lst_row = [lang_lst[i:i + column] for i in range(0, len(lang_lst), column)]
    # розгортання всього списку lang_lst на рядковий список кнопок (по 3 мови)

    kb = InlineKeyboardBuilder()
    # покаток та кінец сторінки
    r_start = page * row
    r_end = (page + 1) * row

    if r_end >= len(lang_lst_row):  # щоб уникнути помилки "list index out of range"
        r_end = len(lang_lst_row)

    # не змінні кнопки з верху
    lang_1 = InlineKeyboardButton(text="first lang", callback_data=f"lang_1")
    lang_2 = InlineKeyboardButton(text="second lang", callback_data=f"lang_2")
    kb.row(lang_1, lang_2)

    # блок змінних кнопок
    for r in range(r_start, r_end):
        page_langs = lang_lst_row[r]
        lang_lst_buttons = [InlineKeyboardButton(text=lang[1], callback_data=f"pag: {lang[0]}") for lang in page_langs]
        kb.row(*lang_lst_buttons)

    # не змінні кнопки з низу
    previous_button = InlineKeyboardButton(text='⬅️', callback_data=f"prev: {page}")
    central_button = InlineKeyboardButton(text="Cancel", callback_data="cancel")
    next_button = InlineKeyboardButton(text='➡️', callback_data=f"next: {page}")
    button_row = [previous_button, central_button, next_button]

    if page == 0:
        del button_row[:1]  # Видалення стрелки вліво
    elif page == number_page:
        button_row.pop()  # Видалення стрелки вправо

    kb.row(*button_row)
    return kb.as_markup()
