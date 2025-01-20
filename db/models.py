__all__ = [
    "User",
    "Base",
]

# Про ORM-паттерн асинхронного sqlalchemy и модели
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm

# декларативная модель базы данных python
# https://metanit.com/python/database/3.2.php
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import JSON, Column, DATE, Integer, VARCHAR, String
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_table"

    user_id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, nullable=True)
    username = Column(VARCHAR(32), unique=False, nullable=False)
    reg_date = Column(DATE, default=datetime.now())
    yadisk_token = Column(String, nullable=True)

class YandexDiskFolder(Base):
    __tablename__ = 'yandex_disk_folders'

    id = Column(Integer, index=True, primary_key=True)
    teacher_id = Column(Integer)
    path = Column(String)
    dates = Column(JSON, nullable=True)