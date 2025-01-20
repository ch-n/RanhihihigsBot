# Файл для хранения секретов

import os
from dotenv import load_dotenv

# предварительно создаем файл .env и помещаем туда Токен
load_dotenv()

# переменные окружения для проекта
TOKEN: str = os.getenv('TOKEN')
CLIENT_ID: str = os.getenv('CLIENT_ID')
TOKEN_URL = f'https://oauth.yandex.ru/authorize?response_type=token&client_id={CLIENT_ID}'