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

    def get_user(self, id):
        row = self._fetch_user(id)
        return User(*row) if row else None

    def update_user(self, id, name):
        user = User(id, name)
        self._update_user_name(user)
        logging.info(f"User {id} updated to name: {user.name}")

    def delete_user(self, id):
        with self.conn:
            self._delete_user_data(id)
        logging.info(f"User {id} and all related data deleted")

    # Helper methods
    def _fetch_user(self, id):
        return self.conn.execute(
            "SELECT id, name FROM users WHERE id = ?", 
            (id,)
        ).fetchone()

    def _update_user_name(self, user):
        self.conn.execute(
            "UPDATE users SET name = ? WHERE id = ?", 
            (user.name, user.id)
        )
        self.conn.commit()

    def _delete_user_data(self, id):
        tables = ['users', 'accounts', 'budgets']
        for table in tables:
            self.conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        self.conn.execute(
            "DELETE FROM transactions WHERE account_id IN (SELECT id FROM accounts WHERE id = ?)", 
            (id,)
        )

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