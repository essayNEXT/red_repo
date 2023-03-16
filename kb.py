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


# InlineKeyboard all languages (додавання мови в Обрані)
def kb_add(lang_dict, column=3, row=5):
    kb = InlineKeyboardBuilder()

    for i, j in lang_dict.items():
        kb.add(InlineKeyboardButton(text=j, callback_data=f'add: {i}'))

    kb.adjust(column)
    paginator = Paginator(data=kb.as_markup(), size=row, dp=router2)
    return paginator()


# Select interface language
def kb_interface(lang_interface):
    print(f'InlineKeyboard Interface input - {lang_interface}')

    kb = InlineKeyboardBuilder()
    for i in lang_interface.keys():
        kb.add(InlineKeyboardButton(text=i, callback_data=f"set: {i}"))

    kb.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return kb.as_markup()


# InlineKeyboard Favorites language
def kb_favor(lang_favor, lst_len=6):
    print(f'InlineKeyboard Favorites input - {lang_favor}')

    kb = InlineKeyboardBuilder()
    for i in lang_favor:
        for j in lang_favor:
            if i != j:
                kb.add(InlineKeyboardButton(text=f'{i} > {j}', callback_data=f"fav: {i},{j}"))
                kb.adjust(lst_len)  # не більше 6 стовпчиків

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
