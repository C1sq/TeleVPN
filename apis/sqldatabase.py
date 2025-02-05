import asyncpg
import asyncio
from datetime import datetime, timedelta
from config import user, password, host, port, dbname


async def insertion(column: str, value_users: str, value_date, telegram_id: str) -> None:
    """
    Обновляет указанный столбец в таблицах users и date для заданного TELEGRAM_ID.
    """
    connection = await create_connection()
    try:
        async with connection.transaction():
            await connection.execute(
                f'''
                INSERT INTO users (TELEGRAM_ID, {column})
                VALUES ($1, $2)
                ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                    {column} = COALESCE(EXCLUDED.{column},users.{column})
                ''',
                telegram_id, value_users
            )
            await connection.execute(
                f'''
                INSERT INTO date (TELEGRAM_ID, {column})
                VALUES ($1, $2)
                ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                    {column} = EXCLUDED.{column}
                ''',
                telegram_id, value_date
            )
    finally:
        await connection.close()


async def get_url(telegram_id: str):
    """
    Получает запись из таблицы users по TELEGRAM_ID и возвращает объект UserRecord.
    Если запись не найдена, возвращает None.
    """
    connection = await create_connection()
    try:
        row = await connection.fetchrow(
            '''
            SELECT * FROM users WHERE TELEGRAM_ID = $1
            ''',
            telegram_id
        )
        '''if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]'''
        return row
    finally:
        await connection.close()


async def get_columns():
    connection = await create_connection()
    try:
        row = await connection.fetchrow(
            '''
            SELECT * FROM users
            '''
        )
        return row
    finally:
        await connection.close()


async def create_connection():
    """
    Создает и возвращает соединение с базой данных.
    """
    return await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=dbname
    )


async def check_and_delete_expired_data():
    """
    Проверяет таблицу date каждые 5 минут и удаляет просроченные значения в таблицах users и subscriptions.
    """
    connection = await create_connection()
    try:
        while True:
            current_time = datetime.now()
            await delete_expired_data(connection, current_time)
            await asyncio.sleep(300)  # Ждём 5 минут
    finally:
        await connection.close()


async def delete_expired_data(connection, current_time):
    """
    Удаляет просроченные записи в таблицах users и subscriptions.
    """
    params = ['TRIAL_NEDERLAND', 'NEDERLAND', 'TRIAL_FRANCE', 'FRANCE', 'TRIAL_GERMANY', 'GERMANY']
    for column in params:
        query = f"""
            SELECT TELEGRAM_ID, {column} FROM date
            WHERE {column}::timestamp < $1;
        """
        expired_entries = await connection.fetch(query, current_time)
        for entry in expired_entries:
            telegram_id = entry['telegram_id']
            await connection.execute(
                f"""
                UPDATE users
                SET {column} = NULL
                WHERE TELEGRAM_ID = $1;
                """,
                telegram_id
            )
            await connection.execute(
                f"""
                UPDATE date
                SET {column} = NULL
                WHERE TELEGRAM_ID = $1;
                """,
                telegram_id
            )


async def check_and_create_table():
    """
    Проверяет наличие таблиц users и date, создает их, если они не существуют.
    """
    connection = await create_connection()
    try:
        result = await connection.fetchrow("SELECT to_regclass('public.users');")
        if result[0] is None:
            print("Таблица users не существует, создаем таблицу...")
            await connection.execute(
                '''
                CREATE TABLE users(
                    id serial PRIMARY KEY,
                    TELEGRAM_ID varchar(20) NOT NULL UNIQUE,
                    TRIAL_NEDERLAND varchar(64),
                    NEDERLAND varchar(64),
                    TRIAL_FRANCE varchar(64),
                    FRANCE varchar(64),
                    TRIAL_GERMANY varchar(64),
                    GERMANY varchar(64)
                )
                '''
            )
        result = await connection.fetchrow("SELECT to_regclass('public.date');")
        if result[0] is None:
            print("Таблица date не существует, создаем таблицу...")
            await connection.execute(
                '''
                CREATE TABLE date(
                    id serial PRIMARY KEY,
                    TELEGRAM_ID varchar(20) NOT NULL UNIQUE,
                    TRIAL_NEDERLAND varchar(64),
                    NEDERLAND varchar(64),
                    TRIAL_FRANCE varchar(64),
                    FRANCE varchar(64),
                    TRIAL_GERMANY varchar(64),
                    GERMANY varchar(64)
                )
                '''
            )
    finally:
        await connection.close()


async def main():
    """
    Основная функция, которая устанавливает соединение с базой данных,
    создает таблицу (если необходимо), вставляет запись и выводит результат.
    """
    try:
        await check_and_create_table()
        await insertion(column='trial_france', telegram_id='2281337', value_users='popa',
                        value_date=str(datetime.now() + timedelta(seconds=10)))
        a = await get_url(telegram_id='2281337')
        print(a)
        asyncio.create_task(check_and_delete_expired_data())
        await asyncio.sleep(10)
    except Exception as e:
        print("Произошла ошибка:", e)


if __name__ == '__main__':
    asyncio.run(main())
