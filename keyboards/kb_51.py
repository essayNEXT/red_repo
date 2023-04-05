from typing import Dict, Iterable, Tuple

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, Dispatcher

from keyboards import localization_manager
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
        super().__init__(data=mutable_keyboard, size=row, dp=dp, *args, **kwargs)
        pass


class KeyboardPaginatorRedTeam51(RedPaginator):

    @staticmethod
    def create_button_tuple_dict(
            upper_or_immutable_buttons: dict | tuple,
            pre: str = None,
            user_id=None) -> list[types.InlineKeyboardButton] | tuple | None:

        def trans_immut_but(user_id, x):
            return str(localization_manager.get_localized_message51(complex_id=user_id, message_key=x))

        if isinstance(upper_or_immutable_buttons, dict):
            return [InlineKeyboardButton(text=trans_immut_but(user_id, text),
                                         callback_data=f'{pre} {callbk.replace(" ", "_").lower()}')
                    for callbk, text in upper_or_immutable_buttons.items()]
        elif isinstance(upper_or_immutable_buttons, tuple):
            return [InlineKeyboardButton(text=trans_immut_but(user_id, text),
                                         callback_data=f'{pre} {text.replace(" ", "_").lower()}')
                    for text in upper_or_immutable_buttons]
        else:
            return upper_or_immutable_buttons
        pass

    def __init__(
            self,
            mutable_keyboard: types.InlineKeyboardMarkup |
                              Iterable[types.InlineKeyboardButton] |
                              Iterable[Iterable[types.InlineKeyboardButton]] |
                              InlineKeyboardBuilder = None,
            mutable_buttons: Dict = None,
            pre: str = None,
            column: int = 3,
            row: int = 5,
            upper_immutable_buttons: Dict | Tuple[str] = None,
            immutable_buttons: Dict | Tuple[str] = None,
            dp: Router = router3,
            user_id: str = None,
            *args, **kwargs):

        super().__init__(
            mutable_keyboard,
            mutable_buttons,
            pre,
            column,
            row,
            dp,
            user_id,
            *args, **kwargs
        )
        if upper_immutable_buttons:  # формування незмінних кнопок upper клави
            upper_immutable_buttons = self.create_button_tuple_dict(upper_immutable_buttons, pre, user_id)
        if immutable_buttons:  # формування незмінних кнопок знизу клави
            immutable_buttons = self.create_button_tuple_dict(immutable_buttons, pre, user_id)
        else:
            immutable_buttons = types.InlineKeyboardButton(text='Cancel', callback_data='cancel')

        self.immutable_buttons = immutable_buttons
        self.upper_immutable_buttons = upper_immutable_buttons
        # super().__init__(data=mutable_keyboard, size=row, dp=dp, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        paginator = super().__call__(*args, **kwargs)
        paginator.inline_keyboard.insert(0, self.upper_immutable_buttons) if self.upper_immutable_buttons else None
        paginator.inline_keyboard.append(self.immutable_buttons) if self.immutable_buttons else None
        return paginator

    #
    #
    #
    #
