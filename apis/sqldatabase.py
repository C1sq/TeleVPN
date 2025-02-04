import psycopg2
from config import user, password, host, port, dbname
import asyncio
from psycopg2.extras import RealDictCursor


class UserRecord:
    def __init__(self, data, columns):
        # Создаем атрибуты для каждого столбца
        for column, value in zip(columns, data):
            setattr(self, column.lower(), value)


async def insertion(connection, telegram_id: str, trial_nederland: str = None, nederland: str = None,
                    trial_france: str = None, france: str = None, trial_germany: str = None,
                    germany: str = None) -> None:
    """
    Вставляет запись в таблицу users. Если запись с таким TELEGRAM_ID уже существует, обновляет поля.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            '''
            INSERT INTO users (TELEGRAM_ID, TRIAL_NEDERLAND, NEDERLAND, TRIAL_FRANCE, FRANCE, TRIAL_GERMANY, GERMANY)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                TRIAL_NEDERLAND = COALESCE(EXCLUDED.TRIAL_NEDERLAND, users.TRIAL_NEDERLAND),
                NEDERLAND = COALESCE(EXCLUDED.NEDERLAND, users.NEDERLAND),
                TRIAL_FRANCE = COALESCE(EXCLUDED.TRIAL_FRANCE, users.TRIAL_FRANCE),
                FRANCE = COALESCE(EXCLUDED.FRANCE, users.FRANCE),
                TRIAL_GERMANY = COALESCE(EXCLUDED.TRIAL_GERMANY, users.TRIAL_GERMANY),
                GERMANY = COALESCE(EXCLUDED.GERMANY, users.GERMANY)
            ''',
            (telegram_id, trial_nederland, nederland, trial_france, france, trial_germany, germany)
        )


def get_url(connection, telegram_id: str):
    """
    Получает запись из таблицы users по TELEGRAM_ID и возвращает объект UserRecord.
    Если запись не найдена, возвращает None.
    """
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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


async def delete_data(connection, telegram_id: str, param: str):
    with connection.cursor() as cursor:
        query = f"""
        UPDATE users
        SET {param} = NULL
        WHERE telegram_id = %s
        """
        cursor.execute(query, (telegram_id,))
        connection.commit()

async def delete_url(mode: str, telegram_id: str, param: str):
    time_mapping = {"30min": 18, "30days": 2592000}  # 1800 секунд = 30 минут
    wait_time = time_mapping.get(mode)

    await asyncio.sleep(wait_time)  # Ждём 30 минут или 30 дней

    connection = create_connection()  # Заново создаем подключение
    connection.autocommit = True

    try:
        await delete_data(connection, telegram_id, param)  # Удаляем данные
    finally:
        connection.close()  # Закрываем соединение



def check_and_create_table(connection):
    """
    Проверяет наличие таблицы users и создает ее, если она не существует.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.users');")
        result = cursor.fetchone()
        if result[0] is None:
            print("Таблица не существует, создаем таблицу...")
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
        print(list(get_columns(connection=connection))[2:])

    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        if connection:
            connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == '__main__':
    asyncio.run(main())
