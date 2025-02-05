import psycopg2
from config import user, password, host, port, dbname
import asyncio
from psycopg2.extras import RealDictCursor


class UserRecord:
    def __init__(self, data, columns):
        # Создаем атрибуты для каждого столбца
        for column, value in zip(columns, data):
            setattr(self, column.lower(), value)


async def insertion(connection, column: str, value_users: str, value_date, telegram_id: str) -> None:
    """
    Обновляет указанный столбец в таблицах users и date для заданного TELEGRAM_ID.
    """
    with connection.cursor() as cursor:
        # Обновление значения в таблице users
        cursor.execute(
            f'''
            INSERT INTO users (TELEGRAM_ID, {column})
            VALUES (%s, %s)
            ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                {column} = COALESCE(EXCLUDED.{column},users.{column})
            ''',
            (telegram_id,value_users)
        )

        # Обновление значения в таблице date
        cursor.execute(
            f'''
            INSERT INTO DATE (TELEGRAM_ID, {column})
            VALUES (%s, %s)
            ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                {column} = EXCLUDED.{column}
            ''',
            (telegram_id, value_date)
        )

    connection.commit()


async def get_url(telegram_id: str):
    """
    Получает запись из таблицы users по TELEGRAM_ID и возвращает объект UserRecord.
    Если запись не найдена, возвращает None.
    """
    connection = create_connection()
    connection.autocommit = True
    with connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor) as cursor:  # cursor_factory=psycopg2.extras.RealDictCursor
        cursor.execute(
            '''
            SELECT * FROM users WHERE TELEGRAM_ID = %s
            ''',
            (telegram_id,)
        )
        row = cursor.fetchone()
        '''if row is None:
            return None

        columns = [desc[0] for desc in cursor.description]'''
        connection.close()
        return row


def get_columns(connection):
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            '''
            SELECT * FROM users 
            '''
        )
        row = cursor.fetchone()
        return row


def create_connection():
    """
    Создает и возвращает соединение с базой данных.
    """
    return psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,  # Убедитесь, что в config.py значение port корректное (например, число 5432 или строка '5432')
        dbname=dbname
    )



from datetime import datetime, timedelta


async def check_and_delete_expired_data():
    """
    Проверяет таблицу date каждые 5 минут и удаляет просроченные значения в таблицах users и subscriptions.
    """
    # Подключение к базе данны
    connection = create_connection()
    connection.autocommit = True

    while True:
        with connection.cursor() as cursor:
            current_time = datetime.now()

            # Проверяем таблицу date на просроченные записи и удаляем их из users и subscriptions
            await delete_expired_data(connection, current_time)

            await asyncio.sleep(300)  # Ждём 5 минут


async def delete_expired_data(connection, current_time):
    """
    Удаляет просроченные записи в таблицах users и subscriptions.
    """
    params = ['TRIAL_NEDERLAND', 'NEDERLAND', 'TRIAL_FRANCE', 'FRANCE', 'TRIAL_GERMANY', 'GERMANY']

    # Обрабатываем каждый столбец для проверки
    for column in params:
        # Формируем запрос для получения просроченных записей
        query = f"""
            SELECT TELEGRAM_ID, {column} FROM date
            WHERE {column}::timestamp < %s;
        """

        # Выполняем запрос
        with connection.cursor() as cursor:
            cursor.execute(query, (current_time,))
            expired_entries = cursor.fetchall()

        # Если есть просроченные записи, обрабатываем их
        for entry in expired_entries:
            telegram_id = entry[0]

            # Удаляем данные из таблицы users
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE users
                    SET {column} = NULL
                    WHERE TELEGRAM_ID = %s;
                    """,
                    (telegram_id,)
                )

            # Удаляем данные из таблицы subscriptions
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE date
                    SET {column} = NULL
                    WHERE TELEGRAM_ID = %s;
                    """,
                    (telegram_id,)
                )

    # Сохраняем изменения в базе данных
    connection.commit()




# Закрываем соединение


def check_and_create_table(connection):
    """
    Проверяет наличие таблиц users и date, создает их, если они не существуют.
    """
    with connection.cursor() as cursor:
        # Проверка и создание таблицы users
        cursor.execute("SELECT to_regclass('public.users');")
        result = cursor.fetchone()
        if result[0] is None:
            print("Таблица users не существует, создаем таблицу...")
            cursor.execute(
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

        # Проверка и создание таблицы date
        cursor.execute("SELECT to_regclass('public.date');")
        result = cursor.fetchone()
        if result[0] is None:
            print("Таблица date не существует, создаем таблицу...")
            cursor.execute(
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
    connection.commit()


async def main():
    """
    Основная функция, которая устанавливает соединение с базой данных,
    создает таблицу (если необходимо), вставляет запись и выводит результат.
    """
    connection = None
    try:
        connection = create_connection()
        connection.autocommit = True

        check_and_create_table(connection)

        # Пример вставки записи
        '''await insertion(connection, telegram_id='87324', trial_germany='aBcw8')

        # Получаем запись и выводим значение поля trial_germany
        us = get_keys(connection, telegram_id='87324')
        print(us)
        if us is not None:
            print("trial_germany =", us['trial_germany'])
        else:
            print("Запись не найдена.")'''
        await insertion(connection=connection,column='trial_france',telegram_id='2281337',value_users='popa',value_date=str(datetime.now()+timedelta(seconds=50)))
        asyncio.create_task(check_and_delete_expired_data())
        await(asyncio.sleep(400))
        print(get_columns(connection))
    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        if connection:
            connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == '__main__':
    asyncio.run(main())
