import asyncio
from datetime import datetime, timedelta
from typing import LiteralString
from urllib.parse import urlparse, urlunparse
from marzban_api_client import AuthenticatedClient
from marzban_api_client.api.user import add_user, get_user, delete_expired_users
from marzban_api_client.models import UserCreateProxies
from marzban_api_client.models.user_response import UserResponse
from marzban_api_client.models.user_create import UserCreate
import random
import string
import requests
from sqldatabase import insertion, create_connection, check_and_create_table, get_keys

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
    print(name, param)

    match param:
        case 'france':
            await insertion(connection=connection, telegram_id=telegram_id, france=name)
        case 'trial_france':
            print(1)
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
        print(token)
        if not token:
            raise ValueError("Ошибка: Неверный логин или пароль")

        self.client = AuthenticatedClient(
            base_url=self.base_url,
            token=token,
            verify_ssl=self.ssl
        )

    async def new_user(self, name: str, data_limit: int = None, days: timedelta = None) -> tuple[
                                                                                               str, LiteralString, datetime | None] | \
                                                                                           tuple[str, LiteralString]:
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
            return short_link, full_link
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
            return short_link, full_link, limit_time

    async def get_trial_subscription(self, telegram_id: str, param: str):
        """Создание временной подписки."""
        name = 'a' + generate_random_string(5)
        connection = create_connection()
        connection.autocommit = True
        check_and_create_table(connection)
        try:
            key = get_keys(connection=connection, telegram_id=telegram_id)['trial_'+param]
            response1: UserResponse = await get_user.asyncio(client=self.client, username=key)
            full_link = '\n'.join(response1.links[:-2:])
            short_link = f'{self.base_url}{response1.subscription_url}'
            print(123)
            return short_link
        except:
            await ins_in_sql(connection=connection, name=name, telegram_id=telegram_id, param=param)
            return await self.new_user(name=name, days=timedelta(minutes=30), data_limit=1073741824)
        finally:
            connection.close()

    async def get_subscription(self, telegram_id: str, param: str):
        """Создание подписки."""
        name = 'a' + generate_random_string(5)
        connection = create_connection()
        connection.autocommit = True
        check_and_create_table(connection)
        try:
            key = get_keys(connection=connection, telegram_id=telegram_id)[param]
            response1: UserResponse = await get_user.asyncio(client=self.client, username=key)
            print(response1)
            full_link = '\n'.join(response1.links[:-2:])
            short_link = f'{self.base_url}{response1.subscription_url}'
            print(123)
            return short_link
        except:
            await ins_in_sql(connection=connection, name=name, telegram_id=telegram_id, param=param)
            return await self.new_user(name=name, days=timedelta(days=30))
        finally:
            connection.close()

    async def delet_exp(self):
        await delete_expired_users.asyncio(client=self.client, expired_before=datetime.now())


# Асинхронный запуск программы
async def main():
    client = Marzipan(
        url=base_url,
        username=yours_username,
        password=yours_password,
        ssl=ssl
    )

    await client.async_init()
    await client.delet_exp()
    print(await client.get_trial_subscription(telegram_id='2281337', param='france'))

    # print( await get_user.asyncio(client=client.client,username='kolya'))


if __name__ == '__main__':
    asyncio.run(main())
