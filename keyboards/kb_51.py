from asyncio import sleep
from typing import Dict, Iterable, Tuple

from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
        kb = InlineKeyboardBuilder()
        kb.row(*upper_immutable_buttons)
        kb.adjust(column)
        upper_immutable_buttons = Paginator(data=kb, dp=dp)

        self.upper_immutable_buttons = upper_immutable_buttons().inline_keyboard
        self.immutable_buttons = immutable_buttons
        # super().__init__(data=mutable_keyboard, size=row, dp=dp, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        paginator = super().__call__(*args, **kwargs)
        if self.upper_immutable_buttons:
            for x in self.upper_immutable_buttons[:-1]:
                paginator.inline_keyboard.insert(0, x)
        # paginator.inline_keyboard.insert(0, self.upper_immutable_buttons) if self.upper_immutable_buttons else None
        paginator.inline_keyboard.extend(self.immutable_buttons) if self.immutable_buttons else None
        return paginator

    async def callback_upper_button(self, callback: CallbackQuery, state: FSMContext):

        async def f_choosing_ok_or_plus(user_dat: dict, curent_state) -> str | int:
            for i_button_f in SET_BUTTONS:
                if not user_dat.get(i_button_f, None):
                    return curent_state + 1
            else:  # якщо всі мови встановлені, цикл пройде до кінця, і виконається цей код
                return "choosing_ok"  # state.set_state(ADDChoice.choosing_ok)

        async def f_message_text(user_dat: dict) -> str:
            return "---".join([user_dat.get(i_button_m, "не вибрано") for i_button_m in SET_BUTTONS])

        #######################################################################################################
        try:
            user_id = str(callback.from_user.id)
            callbk_data = callback.data.split()[1]  # відрізаємо префікс 'add:'
            user_data = await state.get_data()  # порцию {user_data['chosen_food']}
            SET_BUTTONS: tuple = user_data.get("red_buttons")
            SET_BUTTONS: tuple = tuple(x.replace(" ", "_").lower() for x in SET_BUTTONS)
            lang_list: list = user_data.get("langdict")  # список, щоб ловити  в хендлелі
            current_state = user_data.get("red_state")
            # if not current_state: raise
        except:
            callbk_data = 'cancel'
        print(f'callback button  "Add" IN {user_id}, {callbk_data}')
        if callbk_data == 'ok':
            if current_state == "choosing_ok":  # ADDChoice.choosing_ok
                # for i_button_f in SET_BUTTONS:
                #     if not user_data.get(i_button_f, None):
                #         set_langs_flag(user_id, user_data.get(i_button_f), is_active=0)
                # set_langs_flag(user_id, user_data[SET_BUTTONS[0]], user_data[SET_BUTTONS[1]])
                await callback.message.edit_text(text=f'callback button "Add" IN {user_id}, {callbk_data} state OK')
                await sleep(2)
                await callback.message.edit_text(text=f" дякуємо ваш вибір збережено=> "
                                                      + await f_message_text(user_dat=user_data.copy()),
                                                 reply_markup=None)
                await sleep(5)
                await callback.answer("дякуємо ваш вибір збережено " + await f_message_text(user_dat=user_data.copy()))
                await callback.message.delete()
                await state.clear()
                res = "дякуємо ваш вибір збережено " + await f_message_text(user_dat=user_data.copy())
                return res
                ##
            else:  # current_state == ADDChoice.choosing_second_lang or current_state == ADDChoice.choosing_first_lang:
                await callback.message.edit_text(text=f'Ви ще не зробили повністю вибір \n. ')
                # f'callback button "OK" IN {user_id}, {callbk_data} state {current_state}')
                await sleep(2)
                await callback.message.edit_text(
                    text=await f_message_text(user_dat=user_data.copy()),
                    reply_markup=callback.message.reply_markup)  # user_data["reply_markup_link"])

        elif callbk_data == 'cancel':
            print(f'callback button  "cancel" IN {user_id}, {callbk_data}')
            # current_state = await state.get_state()
            await callback.message.edit_text(
                text=f'callback button "cancel" IN {user_id}, {callbk_data}',
                reply_markup=None)
            await sleep(2)
            await callback.answer(" вибір скасовано ")
            await callback.message.delete()
            await state.clear()
        ##################################@router.callback_query(Text(startswith='add:'), ADDChoice.choosing_second_lang)
        elif callbk_data in SET_BUTTONS or callbk_data in lang_list:
            print(f'callback button second "Add" IN {user_id}, {callbk_data}')
            await callback.message.edit_text(text=f'callback "Add" IN {user_id}, {callbk_data}')
            await sleep(2)
            if callbk_data in SET_BUTTONS:  # ["first_lang", 'second_lang']:  # якщо нажали верхні дві кнопки
                await callback.message.edit_text(text=f'зробіть повторно свій вибір')
                if user_data.get(callbk_data, None):
                    del user_data[callbk_data]
                    user_data["red_state"] = SET_BUTTONS.index(
                        callbk_data)  # if current_state == "choosing_ok" else current_state - 1
                    # якщо стате не ОК, тоді -1. Якщо ОК - то міняється на позицію нажатої кнопки
                    # заміна 20рядків коду умови  elif current_state == ADDChoice.choosing_ok
                    # state.set_state(ADDChoice.choosing_first_lang)
                else:
                    await callback.message.edit_text(text=f'Ви ще не вибирали')  # ADDChoice.choosing_first_lang
                await sleep(2)
            else:  # тут вже вибрали  мову    треба придумати алгоритм або карент_стате або перший наступний
                if not user_data.get(SET_BUTTONS[current_state], None):
                    user_data[SET_BUTTONS[current_state]] = callbk_data
                else:
                    for i_button in SET_BUTTONS:
                        if not user_data.get(i_button, None):
                            user_data[i_button] = callbk_data
                            break
                    else:
                        raise  # сюди ніколи не попадає
                user_data["red_state"] = await f_choosing_ok_or_plus(user_dat=user_data.copy(),
                                                                     curent_state=current_state)
                await sleep(2)
            await callback.message.edit_text(text=await f_message_text(user_dat=user_data.copy()),
                                             reply_markup=callback.message.reply_markup)  # user_data["reply_markup_link"])
            await state.set_data({})
            await state.update_data(**user_data)

    #
    #
    #
    #
