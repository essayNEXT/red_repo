from typing import Dict, Iterable, Tuple

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, Dispatcher
from keyboards.paginator_taras import Paginator
from db import get_langs_all, get_langs_activ, get_user_page

router3 = Router()


class RedPaginator(Paginator):

    @staticmethod
    def button_translation(user_id: str, name_buttons: tuple) -> dict:
        result = {}
        for x in name_buttons:
            result.update({x: str(f"{user_id}_lang_{x}")})
        return result

    # @staticmethod
    # def

    def __init__(
            self,
            mutable_keyboard: types.InlineKeyboardMarkup |
                              Iterable[types.InlineKeyboardButton] |
                              Iterable[Iterable[types.InlineKeyboardButton]] |
                              InlineKeyboardBuilder = None,
            mutable_buttons: Dict | tuple = None,
            pre: str = None,
            column: int = 3,
            row: int = 5,
            dp: Router = router3,
            user_id: str = None,
            *args, **kwargs
    ):
        if mutable_buttons and pre:  # формування змінних кнопок клави
            mutable_keyboard = InlineKeyboardBuilder()
            if isinstance(mutable_buttons, tuple):
                mutable_buttons = self.button_translation(user_id, mutable_buttons)
            for callbk, text in mutable_buttons.items():
                mutable_keyboard.add(
                    InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk.replace(" ", "_").lower()}'))

        mutable_keyboard.adjust(column)

        # self.data = mutable_keyboard
        # self.size = row
        # self.dp = dp
        super().__init__(data=mutable_keyboard, size=row, dp=dp, *args, **kwargs)
        pass

    def markup(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)


class KeyboardPaginatorRedTeam(RedPaginator):

    @staticmethod
    def create_button_tuple_dict(
            upper_or_immutable_buttons: dict | tuple,
            pre: str = None) -> Iterable[types.InlineKeyboardButton] | None:

        if isinstance(upper_or_immutable_buttons, dict):
            return [InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk.replace(" ", "_").lower()}')
                    for callbk, text in upper_or_immutable_buttons.items()]
        elif isinstance(upper_or_immutable_buttons, tuple):
            return [InlineKeyboardButton(text=text, callback_data=f'{pre} {text.replace(" ", "_").lower()}')
                    for text in upper_or_immutable_buttons]
        else:
            return upper_or_immutable_buttons
        pass

    def __init__(self, immutable_buttons=None, upper_immutable_buttons=None, pre: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.immutable_buttons = immutable_buttons
        self.upper_immutable_buttons = upper_immutable_buttons

        if upper_immutable_buttons:  # формування незмінних кнопок upper клави
            upper_immutable_buttons = self.create_button_tuple_dict(upper_immutable_buttons, pre)
        if immutable_buttons:  # формування незмінних кнопок знизу клави
            if isinstance(immutable_buttons, dict):
                immutable_buttons = [
                    InlineKeyboardButton(text=text, callback_data=f'{pre} {callbk.replace(" ", "_").lower()}')
                    for callbk, text in immutable_buttons.items()]
            elif isinstance(immutable_buttons, tuple):
                immutable_buttons = [
                    InlineKeyboardButton(text=text, callback_data=f'{pre} {text.replace(" ", "_").lower()}')
                    for text in immutable_buttons]
        else:
            immutable_buttons = types.InlineKeyboardButton(text='Cancel', callback_data='cancel')

    # def kb_add(lang_dict, pre: str, immutable_buttons: dict[str], column=3, row=5):
    """
       Створює inline-клавіатуру Add languages (додавання мови в Обрані)
       :param
       lang_dict: словник текстів для кнопок
            {Lang_code: Lang_name}
       pre: префікс для обробки callback-a
       immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)

       :option column=3, row=5 - число колонок і строк відображення кнопок
            вказані значення по замовчанню
       :return: об'єкт inline-клавіатури
       """
    # kb = InlineKeyboardBuilder()

    # for i, j in lang_dict.items():
    #     kb.add(InlineKeyboardButton(text=j, callback_data=f'{pre} {i}'))
    # from itertools import islice
    # list(iter(lambda: tuple(islice((iter(kb.as_markup().inline_keyboard)), 8)), ()))
    # kb.adjust(column)
    # paginator = RedPaginator(data=kb.as_markup(), size=row, dp=router3)
    # return paginator()
    # return paginator_red_team(mutable_keyboard=kb, immutable_buttons=immutable_buttons, dp=router2)
