# -- Обработчики (handlers) --
# Все обработчики должны быть подключены к маршрутизатору (или диспетчеру)
# Обработчики (handlers) — обработчик сообщений, который будет возвращать другое сообщение, указанное в функции

__all__ = [
    "register_message_handler"
]

# Установить общий уровень логирования и создали экземпляр лога
import logging
from aiogram import Router, types, filters, F
from aiogram.enums import ParseMode
from pydantic import BaseModel
from config import TOKEN_URL
from db import async_session, User
from sqlalchemy import select, insert

from db.models import YandexDiskFolder
from ya_disk_client import YaDiskClient
from .keyboards import keyboard_continue, keyboard_register
from .callbacks import callback_continue, callback_start


# справочная информация
help_string = """
Вас приветствует бот YaDiskBot!
ℹ️ Регистрация — /start
👨🏻‍🦱 Узнать статус пользователя — /status
"""

# настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def command_start_handler(message: types.Message) -> None:
    """Команда регистрации /start"""

    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

        if user is None:
            await message.reply("Выберите вашу роль:", reply_markup=keyboard_register)
        elif user.teacher_id is None:
            await message.reply(f"Ваша роль - преподаватель. Ваш ID для приглашения студентов - {user.user_id}")
        else:
            teacher = await session.get(User, user.teacher_id)
            await message.reply(f"Ваш преподаватель: @{teacher.username}")
            
async def command_status_handler(message: types.Message) -> None:
    """Команда информации о пользователе /status"""

    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

        if user is None:
            await message.reply(text="Зарегистрируйтесь /start")
            return

        text = f"<b>Пользователь</b>: <i>{user.username}</i>\n"

        if user.teacher_id is None:
            text += f"<b>ID приглашение</b>: <i>{user.user_id}</i>\n"
        else:
            text += f"<b>Ваш ID</b>: <i>{user.user_id}</i>\n"

        if user.yadisk_token:
            text += f"<b>Ваш TOKEN Яндекс Диска</b>: <i>{user.yadisk_token}</i>\n"

        if user.teacher_id:
            text += f"<b>Вы закреплены за </b>: <i>@{user.teacher_id}</i>\n"

        await message.reply(text=text, parse_mode="HTML")

async def callback_register_user(message: types.Message):
    teacher_id = int(message.text)

    async with async_session() as session:

        teacher = await session.get(User, teacher_id)
        if teacher is None:
            await message.answer("Преподаватель с таким ID не найден.")
            return

        new_user = User(user_id=message.from_user.id, teacher_id=teacher_id, username=message.from_user.username)
        session.add(new_user)
        await session.commit()
        await session.close()

        logging.info(f"user {message.from_user.id} registered")
        await message.answer(f"Вы зарегистрированы как слушатель у @{teacher.username}")

async def register_command(message: types.Message):
    instructions = (
        "Для регистрации API Яндекс Диска выполните следующие шаги:\n\n"
        f"1. Перейдите по [ссылке]({TOKEN_URL}):\n"
        "2. Авторизируйтесь:\n"
        "3. Cкопируйте ТОКЕН и вставьте его в /token ТОКЕН:\n"
    )

    await message.reply(instructions, parse_mode=ParseMode.MARKDOWN)

async def token_command(message: types.Message):
    async with async_session() as session:

        user = await session.get(User, message.from_user.id)

        if user is None:
            await message.reply("Для добавления токена зарегистрируйтесь как преподаватель")
            return

        if user.teacher_id:
            await message.reply("Добавление токена доступно только преподавателю")
            return

        command_parts = message.text.split()

        if len(command_parts) < 2:
            if user.yadisk_token:
                await message.reply(f"Ваш текущий ТОКЕН = {user.yadisk_token}")
            else:
                await message.reply("Для сохранения токена введите команду в формате `/token ваш_токен`.")

            return

        token = command_parts[1].strip()

        client = YaDiskClient(token=token)
        result = await client.check_token_validity()

        if result:
            user.yadisk_token = token
            await session.commit()
            await message.reply(f"Ваш новый ТОКЕН = {token}")
        else:
            await message.reply(f"Ошибка токена")

async def add_command(message: types.Message):
    async with async_session() as session:

        text = message.text.split()

        if len(text) < 2:
            await message.reply("Укажите путь к папке на Яндекс Диске после команды /add путь_к_папку")
            return

        folder_path = message.text.split()[1].strip()

        user = await session.get(User, message.from_user.id)

        if not user:
            await message.reply("Вы не зарегистрированы. Используйте команду /start для начала")
            return

        if user.teacher_id:
            await message.reply("Команда доступна только преподавателю")
            return

        if not user.yadisk_token:
            await message.reply("У Вас нет токена, используйте команду /token")
            return

        new_folder = YandexDiskFolder(teacher_id=user.id, path=folder_path)
        session.add(new_folder)
        await session.commit()

        await message.reply(f"Папка с путём {folder_path} успешно добавлена в отслеживаемые")

async def delete_command(message: types.Message):
    async with async_session() as session:

        text = message.text.split()

        if len(text) < 2:
            await message.reply("Укажите путь к папке на Яндекс Диске после команды /delete ПУТЬ К ПАПКЕ")
            return

        folder_path = message.text.split()[1].strip()

        user = await session.get(User, message.from_user.id)

        if not user:
            await message.reply("Вы не зарегистрированы. Используйте команду /start для начала")
            return

        if user.teacher_id:
            await message.reply("Команда доступна только преподавателю")
            return

        if not user.yadisk_token:
            await message.reply("У Вас нет токена, используйте команду /token")
            return

        stmt = select(YandexDiskFolder).filter(
            YandexDiskFolder.teacher_id == user.id,
            YandexDiskFolder.path == folder_path
        )
        result = await session.execute(stmt)
        folder = result.scalars().first()

        if not folder:
            await message.reply("Папка с указанным путем не найдена")
            return

        await session.delete(folder)
        await session.commit()

        await message.reply(f"Папка с путём {folder_path} успешно удалена из отслеживаемых")

async def process_unknown_command(message: types.Message) -> None:
    """эхо-ответ"""
    await message.reply(text="Неподдерживаемая команда. Введите /start.")
    logger.info(f"user {message.from_user.id} send unknown message or command!")


async def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(command_start_handler, filters.Command(commands=["start"]))
    router.message.register(command_status_handler, filters.Command(commands=["status"]))
    router.message.register(register_command, filters.Command(commands=["register"]))
    router.message.register(token_command, filters.Command(commands=["token"]))
    router.message.register(add_command, filters.Command(commands=["add"]))
    router.message.register(delete_command, filters.Command(commands=["delete"]))

    router.message.register(callback_register_user)
    router.message.register(process_unknown_command)

    router.callback_query.register(callback_continue, F.data.startswith("continue_"))
    router.callback_query.register(callback_start, lambda c: c.data.startswith('register_'))