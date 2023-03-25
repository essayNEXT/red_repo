from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.paginator import Paginator
from aiogram import Router, types


class InlineKeyboardButton(InlineKeyboardButton):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        print(self.text)
        # self.text = self.text.upper()

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
    def __init__(self, inmutable_keys=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inmutable_keys = inmutable_keys


    def __call__(self, *args, **kwargs):

        paginator = super().__call__( *args, **kwargs)
        paginator.inline_keyboard.append(self.inmutable_keys) if self.inmutable_keys else None
        return paginator


def paginator_red_team(mutable_keyboard, inmutable_keys=None, dp=None, *args, **kwargs):
    # text_button = await localization_manager.get_localized_message(complex_id, "hello")
    inmutable_keys = inmutable_keys or [types.InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    column, row = 3, 5
    mutable_keyboard.adjust(column)

    paginator = KeyboardPaginatorRedTeam(data=mutable_keyboard.as_markup(),
                                         inmutable_keys=inmutable_keys, size=row, dp=dp)
    # paginator = Paginator(data=mutable_keyboard.as_markup(), size=row, dp=dp)
    return paginator()



# ============================== InlineKeyboard Add languages (додавання мови в Обрані) ==========
def kb_add(lang_dict, pre: str, immutable_buttons: tuple[str], column=3, row=5):
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
    # from itertools import islice
    # list(iter(lambda: tuple(islice((iter(kb.as_markup().inline_keyboard)), 8)), ()))
    kb.adjust(column)
    paginator = Paginator(data=kb.as_markup(), size=row, dp=router2)
    return paginator()
    # return paginator_red_team(mutable_keyboard=kb, dp=router2)


# ============================== Select interface language /set ===========================
def kb_interface(lang_interface: list, pre: str, immutable_buttons: tuple[str]) -> InlineKeyboardMarkup:
    """
       Створює inline-клавіатуру зміни мови інтерфейсу,
       :param
       lang_interface: список текстів для кнопок [('uk', 1, 0, 1), ('en', 0, 1, 0), (sq, 0, 0, 0)]
       pre: префікс для обробки callback-a,
       immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)

       :return: об'єкт inline-клавіатури
       """
    print(f'InlineKeyboard Interface input - {lang_interface}')
    kb = InlineKeyboardBuilder()

    for i in lang_interface:  # динамичні кнопки
        kb.add(InlineKeyboardButton(text=i[0], callback_data=f"{pre} {i[0]}"))



     # незмінні кнопки
    # kb.row(*[InlineKeyboardButton(text=i, callback_data=i.lower()) for i in immutable_buttons])
    inmutable_keys = [InlineKeyboardButton(text=i, callback_data=i.lower()) for i in immutable_buttons]
    # return kb.as_markup()
    return paginator_red_team(mutable_keyboard=kb, inmutable_keys=inmutable_keys, dp=router2)


# ================================== InlineKeyboard Favorites language ===================
def kb_favor(lang_favor: list[str], pre: str, immutable_buttons: tuple[str], lst_len: int) -> InlineKeyboardMarkup:
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
                kb.adjust(lst_len)  # Бажано до 6 Обраних мов, не більше 6 стовпчиків

    for i in immutable_buttons:  # незмінні кнопки
        kb.row(InlineKeyboardButton(text=i, callback_data=i.lower()))
    return kb.as_markup()
    # return paginator_red_team(mutable_keyboard=kb, dp=router2)


# ================================== InlineKeyboard Delete language ======================
def kb_del(lang_del: list[str], pre: str, immutable_buttons: tuple[str]) -> InlineKeyboardMarkup:
    """
      Створює inline-клавіатуру видалення мови з Обраних

      :param
      lang_del: список текстів для кнопок
      pre: префікс для обробки callback-a
      immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)

      :return: об'єкт inline-клавіатури
    """

    kb = InlineKeyboardBuilder()
    for i in lang_del:
        kb.add(InlineKeyboardButton(text=i, callback_data=f'{pre} {i}'))

    for i in immutable_buttons:  # незмінні кнопки
        kb.row(InlineKeyboardButton(text=i, callback_data=i.lower()))
    return kb.as_markup()
    # return paginator_red_team(mutable_keyboard=kb, dp=router2)

# ================================== reverse translate ======================
def kb_reverse(buttons: list[str], pre, column=6) -> InlineKeyboardMarkup:
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
        kb.add(InlineKeyboardButton(text=i, callback_data=f'{pre} {i}'))
    kb.adjust(column)
    return kb.as_markup()


