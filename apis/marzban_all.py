import time
from datetime import datetime, timedelta
from http.client import responses
from typing import LiteralString

from marzban_api_client import AuthenticatedClient
from marzban_api_client.api.user import add_user
from marzban_api_client.api.user import get_user
from marzban_api_client.api.subscription import user_subscription_with_client_type
from marzban_api_client.models import UserCreateProxies
from marzban_api_client.models.user_response import UserResponse
from marzban_api_client.models.user_create import UserCreate
import json
import requests
import sys

from marzban_api_client.types import UNSET

base_url = 'URL ON YOUR MARZBAN PANEL'
yours_username = 'USERNAME'
yours_password = 'PASSWORD'
ssl = True

data = {
    'username': yours_username,
    'password': yours_password,
    'grand_type': 'password'
}

client = AuthenticatedClient(
    base_url=base_url,
    token=requests.post(f'{base_url}/api/admin/token', data=data).json().get('access_token'),
    verify_ssl=ssl
)

if client.token == None:
    print(f"Ошибка: Неверный логин или пароль")
    sys.exit(1)


def generate_random_string(length=24):
    import string
    import random
    # Используем буквы (прописные и строчные) и цифры
    characters = string.ascii_letters + string.digits
    # Генерируем строку указанной длины
    return ''.join(random.choices(characters, k=length))


def random_proxies():
    import uuid

    proxi = {'vmess': {'id': str(uuid.uuid4())},
             'vless': {'id': str(uuid.uuid4()), 'flow': ''},
             'trojan': {'password': generate_random_string(24), 'flow': ''},
             'shadowsocks': {'password': generate_random_string(24), 'method': 'chacha20-ietf-poly1305'}}
    return UserCreateProxies.from_dict(proxi)


def new_user(name: str, data_limit: int = None, days: timedelta = None) -> tuple[LiteralString, str, datetime | None] | \
                                                                           tuple[
                                                                               LiteralString, str]:
    limit_time = None
    expire_timestamp = None
    if days:
        limit_time = datetime.now() + days
        expire_timestamp = int(limit_time.timestamp())
    try:
        response1: UserResponse = get_user.sync(client=client, username=name)
        full_link = '\n'.join(response1.links[:-2:])
        short_link = f'{base_url}{response1.subscription_url}'
        return short_link ,'\n',full_link
    except Exception as e:
        user_template = UserCreate(
            username='a'+name,
            data_limit=data_limit,
            proxies=random_proxies(),
            expire=expire_timestamp,

        )
        response: UserResponse = add_user.sync(body=user_template, client=client)
        response1: UserResponse = get_user.sync(client=client, username=user_template.username)
        full_link = '\n'.join(response1.links[:-2:])
        short_link = f'{base_url}{response1.subscription_url}'
        return  short_link, '\n',full_link,'\n',limit_time


def get_trial_subscription():
    return new_user(name=generate_random_string(5), days=timedelta(minutes=30), data_limit=1073741824)


print(new_user('popa228'))
print(get_trial_subscription())
