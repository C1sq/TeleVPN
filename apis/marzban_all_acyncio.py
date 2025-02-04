import asyncio
from datetime import datetime, timedelta
from typing import LiteralString, Any
from urllib.parse import urlparse, urlunparse

from dulwich.porcelain import fetch
from marzban_api_client import AuthenticatedClient
from marzban_api_client.api.user import add_user, get_user, delete_expired_users
from marzban_api_client.models import UserCreateProxies
from marzban_api_client.models.user_response import UserResponse
from marzban_api_client.models.user_create import UserCreate
import random
import string
import requests
from sqldatabase import insertion, create_connection, check_and_create_table, get_url, delete_url

from config_marzban import base_url, yours_username, yours_password, ssl


def symp_url(url: str) -> str:
    parsed_url = urlparse(url)
    short_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    return short_url


def generate_random_string(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def random_proxies():
    import uuid
    proxi = {'vmess': {'id': str(uuid.uuid4())},
             'vless': {'id': str(uuid.uuid4()), 'flow': ''},
             'trojan': {'password': generate_random_string(24), 'flow': ''},
             'shadowsocks': {'password': generate_random_string(24), 'method': 'chacha20-ietf-poly1305'}}
    return UserCreateProxies.from_dict(proxi)


async def ins_in_sql(connection, name: str, telegram_id: str, param: str):
    """params = [
            france,
            trial_france,
            germany,
            trial_germany,
            nederland,
            trial_nederland,

            ]"""

    match param:
        case 'france':
            await insertion(connection=connection, telegram_id=telegram_id, france=name)
        case 'trial_france':
            await insertion(connection=connection, telegram_id=telegram_id, trial_france=name)
        case 'germany':
            await insertion(connection=connection, telegram_id=telegram_id, germany=name)
        case 'trial_germany':
            await insertion(connection=connection, telegram_id=telegram_id, trial_germany=name)
        case 'nederland':
            await insertion(connection=connection, telegram_id=telegram_id, nederland=name)
        case 'trial_nederland':
            await insertion(connection=connection, telegram_id=telegram_id, trial_nederland=name)


class Marzipan:
    def __init__(self, username: str, password: str, ssl: bool, url: str):
        self.client = None
        self.base_url = symp_url(url)
        self.data = {
            'username': username,
            'password': password,
            'grand_type': 'password'
        }
        self.ssl = ssl

    async def async_init(self):
        """Асинхронный метод инициализации для выполнения подключения."""
        token_response = await asyncio.to_thread(
            requests.post,
            f'{self.base_url}/api/admin/token',
            data=self.data
        )
        token = token_response.json().get('access_token')
        if not token:
            raise ValueError("Ошибка: Неверный логин или пароль")

        self.client = AuthenticatedClient(
            base_url=self.base_url,
            token=token,
            verify_ssl=self.ssl
        )

    async def new_user(self, name: str, data_limit: int = None, days: timedelta = None) -> str:
        """Создание нового пользователя."""
        limit_time = None
        expire_timestamp = None
        if days:
            limit_time = datetime.now() + days
            expire_timestamp = int(limit_time.timestamp())

        try:
            response1: UserResponse = await get_user.asyncio(client=self.client, username=name)
            full_link = '\n'.join(response1.links[:-2:])
            short_link = f'{self.base_url}{response1.subscription_url}'
            return short_link
        except Exception:
            user_template = UserCreate(
                username=name,
                data_limit=data_limit,
                proxies=random_proxies(),
                expire=expire_timestamp,
            )
            response: UserResponse = await add_user.asyncio(body=user_template, client=self.client)
            response1: UserResponse = await get_user.asyncio(client=self.client, username=user_template.username)
            full_link = '\n'.join(response1.links[:-2:])
            short_link = f'{self.base_url}{response1.subscription_url}'
            return short_link

    async def get_trial_subscription(self, telegram_id: str, param: str):
        """Создание временной подписки."""
        name = 'a' + generate_random_string(5)
        connection = create_connection()
        connection.autocommit = True
        check_and_create_table(connection)
        param = 'trial_' + param
        try:
            short_link = await get_url(telegram_id=telegram_id)
            short_link = short_link.get(param)
            if short_link is not None:
                return short_link
            else:
                raise
        except:
            short_link = await self.new_user(name=name, days=timedelta(minutes=30))
            await ins_in_sql(connection=connection, name=short_link, telegram_id=telegram_id, param=param)
            asyncio.create_task(
                delete_url(mode='30min', telegram_id=telegram_id, param=param))
            return short_link
        finally:
            connection.close()

    async def get_subscription(self, telegram_id: str, param: str):
        """Создание подписки."""
        name = 'a' + generate_random_string(5)
        connection = create_connection()
        connection.autocommit = True
        check_and_create_table(connection)
        try:
            short_link = await get_url(telegram_id=telegram_id)
            short_link = short_link.get(param)

            if short_link is not None:
                return short_link
            else:
                raise
        except:

            short_link = await self.new_user(name=name, days=timedelta(days=30))
            await ins_in_sql(connection=connection, name=short_link, telegram_id=telegram_id, param=param)
            asyncio.create_task(
                delete_url(mode='30days', telegram_id=telegram_id, param=param))
            return short_link
        finally:
            connection.close()

    async def delete_exp(self):
        await delete_expired_users.asyncio(client=self.client, expired_before=datetime.now())

    '''async def get_key_(self, telegram_id: str) -> list[str | None] | None:
        keys = []
        connection = create_connection()
        connection.autocommit = True
        try:
            keyl = list(get_keys(connection=connection, telegram_id=telegram_id).items())[2:]
            params = [
                'trial_nederland',
                'nederland',
                'trial_france',
                'france',
                'trial_germany',
                'germany',
            ]
            for _, i in keyl:
                
                keys.append(i)

            return keys
        except:
            return None'''


async def get_link(telegram_id: str) -> dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes]:
    links = await get_url(telegram_id=telegram_id)
    return dict(links.items())


# Асинхронный запуск программы
async def main():
    client = Marzipan(
        url=base_url,
        username=yours_username,
        password=yours_password,
        ssl=ssl
    )
    await client.async_init()
    await client.delete_exp()
    print(await client.get_trial_subscription(telegram_id='2281337', param='france'))
    # print(await client.(telegram_id='2281337'))

    # print(await client.get_subscription(telegram_id='2281337', param='france'))
    print(await get_link('2281337'))


if __name__ == '__main__':
    asyncio.run(main())
