from settings import LANGDICT
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


favorites_language = ['en', 'uk', 'ru']

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Favorites language'),
        KeyboardButton(text='All language')]
    ],
    resize_keyboard=True  # зміна ширини та висоти кнопки по ширині екрану
)

# один рядок із трьома кнопками + рядок із кнопкою cancel
keyboard_in = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text='en', callback_data='en'),
        InlineKeyboardButton(text='uk', callback_data='uk'),
        InlineKeyboardButton(text='ru', callback_data='ru')
    ],
    [
        InlineKeyboardButton(text='Cancel', callback_data='cancel')
    ]
    ]
)
# All language
a = 0
keyss = []
keyboard_all = InlineKeyboardMarkup(row_width=4)
for i, j in LANGDICT.items():
    key = InlineKeyboardButton(j, callback_data=i)
    keyss.append(key)
    a += 1
    if a == 4:
        a = 0
        keyboard_all.add(keyss[0], keyss[1], keyss[2], keyss[3])
        keyss = []
print(keyboard_all)
print(keyss)


