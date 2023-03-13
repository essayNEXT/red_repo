from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_inline_paginations.paginator import Paginator
from aiogram import Router

router2 = Router()

# викликаємо ReplyKeyboard (Вибір, додавання, видалення мови)
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Favorites'),
         KeyboardButton(text='Add'),
         KeyboardButton(text='Delete')]
    ],
    resize_keyboard=True,  # зміна ширини та висоти кнопки по ширині екрану
    one_time_keyboard=True  # ховати після використання
)


# InlineKeyboard all languages (для добавления языка в Избранные)
def kb_add(lang_dict, column=3, row=5):
    kb = InlineKeyboardBuilder()

    for i, j in lang_dict.items():
        kb.add(InlineKeyboardButton(text=j, callback_data=f'add: {i}'))

    kb.adjust(column)
    paginator = Paginator(data=kb.as_markup(), size=row, dp=router2)
    return paginator()


# InlineKeyboard Favorites language (flag '01': 'fav' and /set - '00': 'set')
def kb_favor(lang_favor):
    print(lang_favor)

    kb = InlineKeyboardBuilder()
    # Select interface language
    if '00' in lang_favor.keys():
        for i, j in lang_favor.items():
            if i != '00':
                kb.add(InlineKeyboardButton(text=i, callback_data=f"set: {i}"))
    # Select Favorites language
    elif '01' in lang_favor.keys():
        for i, j in lang_favor.items():
            if i != '01':
                kb.add(InlineKeyboardButton(text=i, callback_data=f"fav: {i}"))

    kb.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return kb.as_markup()


# InlineKeyboard Delete language
def kb_del(lang_del):
    print(lang_del)

    kb = InlineKeyboardBuilder()
    for i in lang_del:
        kb.add(InlineKeyboardButton(text=i, callback_data=f'del: {i}'))

    kb.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return kb.as_markup()
