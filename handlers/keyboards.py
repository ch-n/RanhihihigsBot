from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_continue = InlineKeyboardButton(
    text="Далле",
    callback_data="continue_button_pressed"
)

keyboard_continue = InlineKeyboardMarkup(inline_keyboard=[[button_continue]])

teacher_register_button = InlineKeyboardButton(
    text="Преподаватель",
    callback_data="register_teacher",
)

listen_register_button = InlineKeyboardButton(
    text="Слушатель",
    callback_data="register_listener",
)

keyboard_register = InlineKeyboardMarkup(inline_keyboard=[[teacher_register_button, listen_register_button]])