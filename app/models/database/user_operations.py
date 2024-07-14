import logging
import sqlite3
from finance.user import User

class UserOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_user(self, name, email, hashed_password, is_admin=False):
        user = User(None, name, email, hashed_password, is_admin)
        self._execute_query('INSERT INTO users (name, email, hashed_password, is_admin) VALUES (?, ?, ?, ?)',
                            (user.name, user.email, user.password, user.is_admin))
        logging.info(f"User added: {user.name} with email: {user.email}, admin: {user.is_admin}")

    def get_user(self, id):
        row = self._fetch_user(id)
        return User(*row) if row else None

    def get_user_by_name(self, name):
        row = self.conn.execute(
            "SELECT id, name, email, hashed_password, is_admin FROM users WHERE name = ?",
            (name,)
        ).fetchone()
        return User(*row) if row else None

    def get_user_by_email(self, email):
        row = self.conn.execute(
            "SELECT id, name, email, hashed_password, is_admin FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return User(*row) if row else None

    def update_user(self, id, name=None, email=None, hashed_password=None, is_admin=None):
        user = self.get_user(id)
        if not user:
            logging.error(f"User with id {id} not found.")
            return
        if name:
            user.name = name
        if email:
            user.email = email
        if hashed_password:
            user.hashed_password = hashed_password
        if is_admin is not None:
            user.is_admin = is_admin
        self._update_user(user)
        logging.info(f"User {id} updated")

    def delete_user(self, id):
        with self.conn:
            self._delete_user_data(id)
        logging.info(f"User {id} and all related data deleted")

    def get_all_users(self):
        rows = self.conn.execute("SELECT id, name, email, hashed_password, is_admin FROM users").fetchall()
        return [User(*row) for row in rows]

    # Helper methods
    def _fetch_user(self, id):
        return self.conn.execute(
            "SELECT id, name, email, hashed_password, is_admin FROM users WHERE id = ?",
            (id,)
        ).fetchone()

    def _update_user(self, user):
        self.conn.execute(
            "UPDATE users SET name = ?, email = ?, hashed_password = ?, is_admin = ? WHERE id = ?",
            (user.name, user.email, user.hashed_password, user.is_admin, user.id)
        )
        self.conn.commit()

    def _delete_user_data(self, id):
        tables = ['users', 'accounts', 'budgets']
        for table in tables:
            self.conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (id,))
        self.conn.execute(
            "DELETE FROM transactions WHERE account_id IN (SELECT id FROM accounts WHERE user_id = ?)",
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