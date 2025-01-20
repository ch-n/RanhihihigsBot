__all__ = [
    "commands_for_bot"
]

from aiogram import types

bot_commands = (
    ("start", "Регистрация"),
    ("status", "Статус пользователя"),
    ("register", "Инструкцию по регистрации на Яндекс Диске (для преподавателей)"),
    ("token", "Ввод и проверка токена для Яндекс Диска (ля преподавателей)"),
    ("add", "Добавление папки в отслеживаемые для слушателей (для преподавателя,)"),
    ("delete", "Удаление папки из отслеживаемых для слушателей (для преподавателей)")
)

commands_for_bot = []
for cmd, descr in bot_commands:
    commands_for_bot.append(types.BotCommand(command=cmd, description=descr))
