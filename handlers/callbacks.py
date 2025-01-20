from aiogram.types import CallbackQuery
from db import async_session
from db.models import User

async def callback_continue(callback: CallbackQuery):
    """Ответ на кнопку продолжить"""

    async with async_session() as session:
        # Что-то проиходит
        await session.commit()
    await callback.message.answer("Успешно!")

async def callback_start(callback: CallbackQuery):
    await callback.answer()
    role = callback.data.split("_")[1] 

    async with async_session() as session:
        if role == "teacher":
            new_user = User(user_id=callback.from_user.id, username=callback.from_user.username)
            session.add(new_user)
            await session.commit()
            await callback.message.answer(f"Ваш ID для приглашения студентов {new_user.user_id}")
        else:
            await callback.message.answer("Введите ID вашего преподавателя:")
