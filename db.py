""" database access for guestbook
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import os
from flask import current_app
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ["DATABASE_URL"]
    current_app.logger.info("Creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode="require")

@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

# === Guestbook-specific functions ===

def add_guest(name, message):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding guest %s", name)
        cur.execute(
            "INSERT INTO guests (guest_name, guest_message) VALUES (%s, %s)",
            (name, message),
        )

def get_guests(page=0, per_page=10):
    limit = per_page
    offset = page * per_page
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT * FROM guests ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return cur.fetchall()