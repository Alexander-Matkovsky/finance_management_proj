# user_operations.py
import logging
import sqlite3
from finance.user import User

class UserOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_user(self, name):
        user = User(None, name)
        self._execute_query('INSERT INTO users (name) VALUES (?)', (user.name,))
        logging.info(f"User added: {user.name}")

    def get_user(self, user_id):
        row = self.conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        return User(*row) if row else None

    def update_user(self, user_id, name):
        user = User(user_id, name)
        self.conn.execute("UPDATE users SET name = ? WHERE id = ?", (user.name, user.user_id))
        self.conn.commit()
        logging.info(f"User {user_id} updated to name: {user.name}")

    def delete_user(self, user_id):
        with self.conn:
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM transactions WHERE account_id IN (SELECT id FROM accounts WHERE user_id = ?)", (user_id,))
        logging.info(f"User {user_id} and all related data deleted")

    def _execute_query(self, query, params=()):
        try:
            with self.conn:
                self.conn.execute(query, params)
        except sqlite3.IntegrityError as e:
            logging.error(f"IntegrityError: {e}")
            raise
        except sqlite3.OperationalError as e:
            logging.error(f"OperationalError: {e}")
            raise
