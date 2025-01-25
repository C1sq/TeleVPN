import asyncio
from datetime import datetime, timedelta
from typing import LiteralString

from marzban_api_client import AuthenticatedClient
from marzban_api_client.api.user import add_user
from marzban_api_client.api.user import get_user
from marzban_api_client.models import UserCreateProxies
from marzban_api_client.models.user_response import UserResponse
from marzban_api_client.models.user_create import UserCreate
import random
import string
import sys
import requests

base_url = 'URL ON YOUR MARZBAN PANEL'
yours_username = 'USERNAME'
yours_password = 'PASSWORD'
ssl = True

data = {
    'username': yours_username,
    'password': yours_password,
    'grand_type': 'password'
}

# Создание клиента для работы с API Marzban
client = AuthenticatedClient(
    base_url=base_url,
    token=requests.post(f'{base_url}/api/admin/token', data=data).json().get('access_token'),
    verify_ssl=ssl
)

if client.token is None:
    print(f"Ошибка: Неверный логин или пароль")
    sys.exit(1)

# Функция для генерации случайных строк
def generate_random_string(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Функция для создания случайных прокси
def random_proxies():
    import uuid
    proxi = {'vmess': {'id': str(uuid.uuid4())},
             'vless': {'id': str(uuid.uuid4()), 'flow': ''},
             'trojan': {'password': generate_random_string(24), 'flow': ''},
             'shadowsocks': {'password': generate_random_string(24), 'method': 'chacha20-ietf-poly1305'}}
    return UserCreateProxies.from_dict(proxi)

# Асинхронная функция для создания нового пользователя
async def new_user(name: str, data_limit: int = None, days: timedelta = None) -> tuple[str,LiteralString, datetime | None] | \
                                                                           tuple[str,
                                                                               LiteralString]:
    limit_time = None
    expire_timestamp = None
    if days:
        limit_time = datetime.now() + days
        expire_timestamp = int(limit_time.timestamp())

    try:
        response1: UserResponse = await get_user.asyncio(client=client, username=name)
        full_link = '\n'.join(response1.links[:-2:])
        short_link = f'{base_url}{response1.subscription_url}'
        return short_link ,full_link
    except Exception as e:
        user_template = UserCreate(
            username='a'+name,
            data_limit=data_limit,
            proxies=random_proxies(),
            expire=expire_timestamp,
        )
        response: UserResponse = await add_user.asyncio(body=user_template, client=client)
        response1: UserResponse = await get_user.asyncio(client=client, username=user_template.username)
        full_link = '\n'.join(response1.links[:-2:])
        short_link = f'{base_url}{response1.subscription_url}'
        return short_link, full_link, limit_time

# Асинхронная функция для получения пробной подписки
async def get_trial_subscription():
    return await new_user(name=generate_random_string(5), days=timedelta(minutes=30), data_limit=1073741824)

# Основная асинхронная функция, которая запускает задачи
async def main():
    # Пример создания нового пользователя
    print('popa',await new_user('popa228'))
    # Пример получения пробной подписки
    print(await get_trial_subscription())

# Запуск основной программы
if __name__ == "__main__":
    asyncio.run(main())
