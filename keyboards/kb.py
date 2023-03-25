from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types
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


# ============================== InlineKeyboard ADD Paginator Taras =========================
def kb_add(lang_dict, pre: str, immutable_buttons: tuple[str], column=3, row=5):
    """
       Створює inline-клавіатуру Add languages (додавання мови в Обрані)
       :param
       lang_dict: словник текстів для кнопок
            {Lang_code: Lang_name}
       pre: префікс для обробки callback-a
       immutable_buttons: список назв до незмінних кнопок (наприклад, "Скасувати",)

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

    # незмінні кнопки      callback_data=i.lower() - що при перекладі?
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


# ========================================= ADD NEW ==============================
def kb_add_my(user_id, page=0, row=5, column=3) -> InlineKeyboardMarkup:
    # перевіряєм чи існує запис в табл. page
    myresult = get_user_page(user_id)
    if myresult:
        page = myresult[0]

    # отримуємо з БД список обраних мов (щоб виключити їх зі списку мов, які можно додати)
    lst = get_langs_activ(user_id)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    print(f' in Favorites {lst}')

    # отримуємо з БД словник доступних мов
    lang_dict = get_langs_all()

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
    r_start = page * row
    r_end = (page + 1) * row

    if r_end >= len(lang_lst_row):  # щоб уникнути помилки "list index out of range"
        r_end = len(lang_lst_row)

    for r in range(r_start, r_end):
        page_langs = lang_lst_row[r]
        lang_lst_buttons = [InlineKeyboardButton(text=lang[1], callback_data=f"pag: {lang[0]}") for lang in page_langs]
        kb.row(*lang_lst_buttons)

    previous_button = InlineKeyboardButton(text='⬅️', callback_data=f"prev: {page}")
    central_button = InlineKeyboardButton(text="Cancel", callback_data="cancel")
    next_button = InlineKeyboardButton(text='➡️', callback_data=f"next: {page}")
    button_row = [previous_button, central_button, next_button]

    if page == 0:
        del button_row[:1]              # Видалення стрелки вліво
    elif page == number_page:
        button_row.pop()                 # Видалення стрелки вправо

    kb.row(*button_row)
    return kb.as_markup()
