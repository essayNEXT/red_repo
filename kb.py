from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_inline_paginations.paginator import Paginator
from aiogram import Router


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

# викликаємо ReplyKeyboard (Вибір, додавання, видалення мови) - old
# keyboard = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text='Favorites'),
#          KeyboardButton(text='Add'),
#          KeyboardButton(text='Delete')]
#     ],
#     resize_keyboard=True,  # зміна ширини та висоти кнопки по ширині екрану
#     one_time_keyboard=True  # ховати після використання
# )


# ============================== InlineKeyboard Add languages (додавання мови в Обрані) ==========
def kb_add(lang_dict, pre: str, text_cancel: str, column=3, row=5):
    """
       Створює inline-клавіатуру Add languages
       :param
       lang_dict: словник текстів для кнопок
            {Lang_code: Lang_name}
       pre: префікс для обробки callback-a
       text_cancel: напис на кнопці "Скасувати"

       :option column=3, row=5 - чмсло колонок і строк відображення кнопок
            вказані значення по замовчанню
       :return: об'єкт inline-клавіатури
       """
    kb = InlineKeyboardBuilder()

    for i, j in lang_dict.items():
        kb.add(InlineKeyboardButton(text=j, callback_data=f'{pre} {i}'))

    kb.adjust(column)
    paginator = Paginator(data=kb.as_markup(), size=row, dp=router2)
    return paginator()


# ============================== Select interface language ===========================
def kb_interface(lang_interface: dict, pre: str, text_cancel: str) -> InlineKeyboardMarkup:
    """
       Створює inline-клавіатуру зміни мови інтерфейсу,
       :param
       lang_interface: словник текстів для кнопок
            {'uk': 1, 'en':0} - {Lang_code: Lang_interface},
       pre: префікс для обробки callback-a,
       text_cancel: напис на кнопці "Скасувати",

       :return: об'єкт inline-клавіатури
       """
    print(f'InlineKeyboard Interface input - {lang_interface}')
    kb = InlineKeyboardBuilder()
    for i in lang_interface.keys():
        kb.add(InlineKeyboardButton(text=i, callback_data=f"{pre} {i}"))

    kb.row(InlineKeyboardButton(text=text_cancel, callback_data='cancel'))
    return kb.as_markup()


# ================================== InlineKeyboard Favorites language ===================
def kb_favor(lang_favor: list[str], pre: str, text_cancel: str, lst_len: int) -> InlineKeyboardMarkup:
    """
      Створює inline-клавіатуру Обраних мов
      Бажано до 6 мов (щоб мови не перемішувалися),
      одна source-мова - один ряд)

      :param
      lang_favor: список текстів для кнопок
      pre: префікс для обробки callback-a
      text_cancel: напис на кнопці "Скасувати"
      lst_len: кількість мов у ряду

      :return: об'єкт inline-клавіатури
    """

    print(f'InlineKeyboard Favorites input - {lang_favor}')
    kb = InlineKeyboardBuilder()
    for i in lang_favor:
        for j in lang_favor:
            if i != j:
                kb.add(InlineKeyboardButton(text=f'{i} > {j}', callback_data=f"{pre} {i}>{j}"))
                kb.adjust(lst_len)  # Бажано до 6 Обраних мов, не більше 6 стовпчиків

    kb.row(InlineKeyboardButton(text=text_cancel, callback_data='cancel'))
    return kb.as_markup()


# ================================== InlineKeyboard Delete language ======================
def kb_del(lang_del: list[str], pre: str, text_cancel: str) -> InlineKeyboardMarkup:
    """
      Створює inline-клавіатуру видалення мови з Обраних

      :param
      lang_del: список текстів для кнопок
      pre: префікс для обробки callback-a
      text_cancel: напис на кнопці "Скасувати"

      :return: об'єкт inline-клавіатури
    """
    print(lang_del)
    kb = InlineKeyboardBuilder()
    for i in lang_del:
        kb.add(InlineKeyboardButton(text=i, callback_data=f'{pre} {i}'))

    kb.row(InlineKeyboardButton(text=text_cancel, callback_data='cancel'))
    return kb.as_markup()
