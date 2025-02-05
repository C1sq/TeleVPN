import asyncpg
import asyncio
from datetime import datetime, timedelta
from config import user,password,host,port,dbname

class UserRecord:
    def __init__(self, data, columns):
        # Создаем атрибуты для каждого столбца
        for column, value in zip(columns, data):
            setattr(self, column.lower(), value)


async def insertion(connection, column: str, value_users: str, value_date, telegram_id: str) -> None:
    """
    Обновляет указанный столбец в таблицах users и date для заданного TELEGRAM_ID.
    """
    async with connection.transaction():
        # Обновление значения в таблице users
        await connection.execute(
            f'''
            INSERT INTO users (TELEGRAM_ID, {column})
            VALUES ($1, $2)
            ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                {column} = COALESCE(EXCLUDED.{column},users.{column})
            ''',
            telegram_id, value_users
        )

        # Обновление значения в таблице date
        await connection.execute(
            f'''
            INSERT INTO date (TELEGRAM_ID, {column})
            VALUES ($1, $2)
            ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                {column} = EXCLUDED.{column}
            ''',
            telegram_id, value_date
        )


async def get_url(connection, telegram_id: str):
    """
    Получает запись из таблицы users по TELEGRAM_ID и возвращает объект UserRecord.
    Если запись не найдена, возвращает None.
    """
    row = await connection.fetchrow(
        '''
        SELECT * FROM users WHERE TELEGRAM_ID = $1
        ''',
        telegram_id
    )
    if row is None:
        return None
    columns = row.keys()
    return UserRecord(row.values(), columns)


async def get_columns(connection):
    row = await connection.fetchrow(
        '''
        SELECT * FROM users
        '''
    )
    return row


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


async def check_and_delete_expired_data(connection):
    """
    Проверяет таблицу date каждые 5 минут и удаляет просроченные значения в таблицах users и subscriptions.
    """
    while True:
        current_time = datetime.now()

        await delete_expired_data(connection, current_time)

        await asyncio.sleep(300)  # Ждём 5 минут


async def delete_expired_data(connection, current_time):
    """
    Удаляет просроченные записи в таблицах users и subscriptions.
    """
    params = ['TRIAL_NEDERLAND', 'NEDERLAND', 'TRIAL_FRANCE', 'FRANCE', 'TRIAL_GERMANY', 'GERMANY']

    # Обрабатываем каждый столбец для проверки
    for column in params:
        query = f"""
            SELECT TELEGRAM_ID, {column} FROM date
            WHERE {column}::timestamp < $1;
        """

        expired_entries = await connection.fetch(query, current_time)

        # Если есть просроченные записи, обрабатываем их
        for entry in expired_entries:
            telegram_id = entry['telegram_id']

            # Удаляем данные из таблицы users
            await connection.execute(
                f"""
                UPDATE users
                SET {column} = NULL
                WHERE TELEGRAM_ID = $1;
                """,
                telegram_id
            )

            # Удаляем данные из таблицы subscriptions
            await connection.execute(
                f"""
                UPDATE date
                SET {column} = NULL
                WHERE TELEGRAM_ID = $1;
                """,
                telegram_id
            )


async def check_and_create_table(connection):
    """
    Проверяет наличие таблиц users и date, создает их, если они не существуют.
    """
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


async def main():
    """
    Основная функция, которая устанавливает соединение с базой данных,
    создает таблицу (если необходимо), вставляет запись и выводит результат.
    """
    connection = None
    try:
        connection = await create_connection()

        await check_and_create_table(connection)

        # Пример вставки записи
        await insertion(connection, column='trial_france', telegram_id='2281337', value_users='popa',
                        value_date=str(datetime.now() + timedelta(seconds=10)))

        asyncio.create_task(check_and_delete_expired_data(connection))
        await asyncio.sleep(100)

        columns = await get_columns(connection)
        print(columns)
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        if connection:
            await connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == '__main__':
    asyncio.run(main())
