from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_inline_paginations.paginator import Paginator
from aiogram import Router, types

router2 = Router()


class KeyboardPaginatorRedTeam(Paginator):
    def __init__(self, inmutable_keyboard=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inmutable_keyboard = inmutable_keyboard

    def __call__(self, *args, **kwargs):
        def _is_only_one_page(keyboard):
            result = False
            for button in keyboard:
                if button.text == f"1{self.page_separator}1":
                    result = True
                else:
                    result = False
            return result

        paginator = super().__call__( *args, **kwargs)
        if len(paginator.inline_keyboard[-1]) == 1 and _is_only_one_page(paginator.inline_keyboard[-1]):
            paginator.inline_keyboard.pop()
        paginator.inline_keyboard.append(self.inmutable_keyboard) if self.inmutable_keyboard else None
        return paginator


def paginator_red_team(mutable_keyboard, inmutable_keyboard=None, dp=None, *args, **kwargs):
    # text_button = await localization_manager.get_localized_message(complex_id, "hello")
 #   inmutable_keyboard = inmutable_keyboard or [types.InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    column, row = 3, 5
    mutable_keyboard.adjust(column)
    # paginator = KeyboardPaginatorRedTeam(data=mutable_keyboard.as_markup(),
    #                                      inmutable_keyboard=inmutable_keyboard, size=row, dp=dp)
    paginator = Paginator(data=mutable_keyboard.as_markup(), size=row, dp=dp)
    return paginator()


# InlineKeyboard all languages (додавання мови в Обрані)
def kb_add(lang_dict):
    kb = InlineKeyboardBuilder()
    for i, j in lang_dict.items():
        kb.add(InlineKeyboardButton(text=j, callback_data=f'add: {i}'))
    return paginator_red_team(mutable_keyboard=kb, dp=router2)


# Select interface language
def kb_interface(lang_interface):
    print(f'InlineKeyboard Interface input - {lang_interface}')

    kb = InlineKeyboardBuilder()
    for i in lang_interface.keys():
        kb.add(InlineKeyboardButton(text=i, callback_data=f"set: {i}"))
    return paginator_red_team(mutable_keyboard=kb, dp=router2)


# InlineKeyboard Favorites language
def kb_favor(lang_favor):
    print(f'InlineKeyboard Favorites input - {lang_favor}')
    kb = InlineKeyboardBuilder()
    for i in lang_favor:
        for j in lang_favor:
            if i != j:
                kb.add(InlineKeyboardButton(text=f'{i} > {j}', callback_data=f"fav: {i},{j}"))
    return paginator_red_team(mutable_keyboard=kb, dp=router2)


# InlineKeyboard Delete language
def kb_del(lang_del):
    print(lang_del)
    kb = InlineKeyboardBuilder()
    for i in lang_del:
        kb.add(InlineKeyboardButton(text=i, callback_data=f'del: {i}'))
    return paginator_red_team(mutable_keyboard=kb, dp=router2)


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
