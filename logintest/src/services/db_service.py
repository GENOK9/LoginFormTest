import psycopg2
from psycopg2 import sql, pool
import os
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()
class DBService:
    def __init__(self):
        self.db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections at the same time
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

    def fetch_user_password(self, email: str) -> Optional[Tuple[str]]:
        conn = self.db_pool.getconn()
        cur = conn.cursor()
        query = sql.SQL("SELECT password FROM users WHERE email = %s")
        cur.execute(query, (email,))

        result = cur.fetchone()

        cur.close()
        conn.close()
        self.db_pool.putconn(conn)

        return result

    def fetch_user_id_by_email(self, email: str) -> Optional[Tuple[int]]:
        conn = self.db_pool.getconn()
        cur = conn.cursor()
        query = sql.SQL("SELECT id FROM users WHERE email = %s")
        cur.execute(query, (email,))

        result = cur.fetchone()

        cur.close()
        conn.close()
        self.db_pool.putconn(conn)
        return result