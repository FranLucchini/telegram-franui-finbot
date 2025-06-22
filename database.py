import datetime
import sqlite3

import pytz


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT
            )
        ''')
        self.conn.commit()

    def _get_current_timestamp(self):
        # Set the time zone to Santiago, Chile
        santiago_tz = pytz.timezone('America/Santiago')
        # Get the current date and time in Santiago
        current_date = datetime.datetime.now(santiago_tz)
        return current_date

    def insert_expense(self, category, amount, description):
        # Get current date at santiago chile timezone
        date = self._get_current_timestamp()
        self.cursor.execute(
            '''
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        ''', (date, category, amount, description),
        )
        self.conn.commit()

    def get_expenses(self):
        self.cursor.execute('SELECT * FROM expenses')
        return self.cursor.fetchall()

    def get_expenses_by_month(self, month, year):
        self.cursor.execute(
            '''
            SELECT * FROM expenses
            WHERE STRFTIME('%Y', date) = ? AND STRFTIME('%m', date) = ?
        ''', (year, month),
        )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
