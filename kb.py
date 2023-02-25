from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Select target language')]
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
