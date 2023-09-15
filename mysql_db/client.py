import os

from dotenv import load_dotenv
from mysql.connector import connect


class MySQLClient:
    def __init__(
        self,
        host: str = None,
        database: str = None,
        login: str = None,
        password: str = None,
    ):
        load_dotenv()
        self.host = host or os.environ.get("DB_HOST")
        self.database = database or os.environ.get("DB_DATABASE")
        self.login = login or os.environ.get("DB_LOGIN")
        self.password = password or os.environ.get("DB_PASSWORD")

    def connection(self):
        return connect(
            host=self.host,
            database=self.database,
            user=self.login,
            password=self.password,
        )

    def execute_query(self, query: str, commit: bool = True):
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            if commit:
                conn.commit()
