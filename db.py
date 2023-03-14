import base64
import os
import sqlite3


BOLUO_DB_PATH = os.path.expanduser('~/.hoshino/boluomi.db')
class BoluoCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(BOLUO_DB_PATH), exist_ok=True)
        self._create_table()
        self._create_index()

    def _connect(self):
        return sqlite3.connect(BOLUO_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''
            CREATE TABLE IF NOT EXISTS BOLUO_DATA(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                BOLUO_NAME        TEXT   NOT NULL,
                BOLUO_PIC        TEXT   NOT NULL,
                BOLUO_TYPE        TEXT   NOT NULL,
                BOLUO_TIME        TEXT   NOT NULL,
                BOLUO_TITEL       TEXT   NOT NULL,
                BOLUO_URL         TEXT   NOT NULL
                );''')
        except Exception as e:
            raise e

    def _create_index(self):
        try:
            self._connect().execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS indexname ON
                BOLUO_DATA (
                BOLUO_NAME,BOLUO_TYPE
                );''')
        except Exception as e:
            raise e

    def _add_boluo(self, boluo_name, boluo_pic, boluo_type, boluo_time, boluo_titel, boluo_url): #增加数据
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO BOLUO_DATA (BOLUO_NAME, BOLUO_PIC, BOLUO_TYPE, BOLUO_TIME, BOLUO_TITEL, BOLUO_URL) \
                                VALUES (?,?,?,?,?,?)", [boluo_name, boluo_pic, boluo_type, boluo_time, boluo_titel, boluo_url]
                )
        except Exception as e:
            raise e

    def _get_boluo_data(self, boluo_name):
        try:
            r = self._connect().execute("SELECT BOLUO_NAME, BOLUO_PIC, BOLUO_TYPE, BOLUO_TIME, BOLUO_TITEL, BOLUO_URL FROM BOLUO_DATA WHERE BOLUO_NAME=?", [boluo_name]).fetchall()
            return [] if r is None else r
        except Exception as e:
            raise e

    def _like_boluo_data(self, boluo_msg):
        try:
            r = self._connect().execute(f"SELECT BOLUO_NAME, BOLUO_PIC, BOLUO_TYPE, BOLUO_TIME, BOLUO_TITEL, BOLUO_URL FROM BOLUO_DATA WHERE BOLUO_NAME LIKE '%{boluo_msg}%' OR BOLUO_TITEL LIKE '%{boluo_msg}%' COLLATE NOCASE").fetchall()
            return [] if r is None else r
        except Exception as e:
            raise e



def add_boluo(boluo_name, boluo_pic, boluo_type, boluo_time, boluo_titel, boluo_url):
    PC = BoluoCounter()
    PC._add_boluo(boluo_name, boluo_pic, boluo_type, boluo_time, boluo_titel, boluo_url)


def get_boluo(boluo_name):
    PC = BoluoCounter()
    R = PC._get_boluo_data(boluo_name)
    print(R)

def like_boluo(boluo_msg):
    PC = BoluoCounter()
    R = PC._like_boluo_data(boluo_msg)
    return R


