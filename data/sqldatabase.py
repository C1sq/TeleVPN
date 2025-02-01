import psycopg2
from psycopg2 import sql, Error
from config import user, password, host, port, dbname

try:

    # Параметры подключения
    connection = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.users1');")
        result = cursor.fetchone()
        if result[0] is None:
            # Если таблица не существует, создаем её
            print("Таблица не существует, создаем таблицу...")
            cursor.execute(
                '''
                CREATE TABLE users1(
                id serial PRIMARY KEY,
                TELEGRAM_ID varchar(20) NOT NULL UNIQUE,
                TRIAL_NEDERLAND varchar(6),
                NEDERLAND varchar(6),
                TRIAL_FRANCE varchar(6),
                FRANCE varchar(6),
                TRIAL_GERMANY varchar(6),
                GERMANY varchar(6))
                '''
            )


    # insert
    def insertion(telegram_id: str, trial_nederland: str = None, nederland: str = None, trial_france: str = None,
                  france: str = None, trial_germany: str = None, germany: str = None) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO users1 (TELEGRAM_ID, TRIAL_NEDERLAND, NEDERLAND, TRIAL_FRANCE, FRANCE, TRIAL_GERMANY, GERMANY)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (TELEGRAM_ID) DO UPDATE SET
                    TRIAL_NEDERLAND = COALESCE(EXCLUDED.TRIAL_NEDERLAND, users1.TRIAL_NEDERLAND),
                    NEDERLAND = COALESCE(EXCLUDED.NEDERLAND, users1.NEDERLAND),
                    TRIAL_FRANCE = COALESCE(EXCLUDED.TRIAL_FRANCE, users1.TRIAL_FRANCE),
                    FRANCE = COALESCE(EXCLUDED.FRANCE, users1.FRANCE),
                    TRIAL_GERMANY = COALESCE(EXCLUDED.TRIAL_GERMANY, users1.TRIAL_GERMANY),
                    GERMANY = COALESCE(EXCLUDED.GERMANY, users1.GERMANY)
                ''',
                (telegram_id, trial_nederland, nederland, trial_france, france, trial_germany, germany)
            )


    class UserRecord:
        def __init__(self, data, columns):
            # Создаем атрибуты для каждого столбца
            for column, value in zip(columns, data):
                setattr(self, column.lower(), value)


    def get_keys(telegram_id: str):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT * FROM users1 WHERE TELEGRAM_ID = %s
                ''',
                (telegram_id,)
            )
            row = cursor.fetchone()  # Получаем первую строку
            if row is None:
                return None  # Если нет данных, возвращаем None

            columns = [desc[0] for desc in cursor.description]

            # Создаем объект UserRecord с динамическими аттрибутами
            return UserRecord(row, columns)
finally:
    '''insertion(telegram_id='87324', trial_germany='aBcw8')
    us = get_keys(telegram_id='87324')
    print(us.trial_germany)'''
    # Закрываем соединение
    if connection:
        connection.close()
        print("Соединение с PostgreSQL закрыто")
