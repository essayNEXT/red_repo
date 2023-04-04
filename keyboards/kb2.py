from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message


class PaginationInlineKeyboard:
    def __init__(self, langs: list, page_size: int = 4):
        self.langs = langs
        self.page_size = page_size
        self.page_count = (len(langs) + page_size - 1) // page_size
        self.current_page = 0
        self.keyboard_markup = InlineKeyboardMarkup()
        self.build_keyboard()

    def build_keyboard(self):
        self.keyboard_markup = InlineKeyboardMarkup()
        lang_buttons = [InlineKeyboardButton(text=lang, callback_data=str(index)) for index, lang in
                          enumerate(self.get_current_page())]
        previous_button = InlineKeyboardButton(text="⬅️", callback_data="previous")
        next_button = InlineKeyboardButton(text="➡️", callback_data="next")
        button_row = lang_buttons + [previous_button, next_button]
        self.keyboard_markup.row(*button_row)

    def get_current_page(self):
        start = self.current_page * self.page_size
        end = (self.current_page + 1) * self.page_size
        return self.langs[start:end]

    async def handle_callback_query(self, query: CallbackQuery, state: FSMContext):
        query_data = query.data

        if query_data == "previous":
            self.current_page = max(self.current_page - 1, 0)
            self.build_keyboard()

        elif query_data == "next":
            self.current_page = min(self.current_page + 1, self.page_count - 1)
            self.build_keyboard()

        else:
            await self.lang_callback_action(query_data, query, state)

        await query.message.edit_reply_markup(reply_markup=self.keyboard_markup)

    async def lang_callback_action(self, query_data: str, query: CallbackQuery, state: FSMContext):
        pass  # Your implementation for handling individual lang callbacks goes here




async def start_command_handler(message: Message, state: FSMContext):
    langs = ["lang 1", "lang 2", "lang 3", "lang 4", "lang 5", "lang 6", "lang 7"]
    keyboard = PaginationInlineKeyboard(langs)
    await message.answer("Here's your keyboard:", reply_markup=keyboard.keyboard_markup)
    await state.set_state("menu")


async def lang_callback_action(query_data: str, query: CallbackQuery, state: FSMContext):
    
    # Моя реалізація для обробки індивідуальних зворотних викликів опціонів знаходиться тут
    lang = langs[int(query_data)]
    await query.answer("You selected: " + lang)



