import logging
import sqlite3
from finance.user import User

class UserOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_user(self, name, email, hashed_password):
        user = User(None, name, email, hashed_password)
        self._execute_query('INSERT INTO users (name, email, hashed_password) VALUES (?, ?, ?)', 
                            (user.name, user.email, user.hashed_password))
        logging.info(f"User added: {user.name} with email: {user.email}")

    def get_user(self, id):
        row = self._fetch_user(id)
        return User(*row) if row else None
    
    def get_user_by_name(self, name):
        row = self.conn.execute(
            "SELECT id, name, email, hashed_password FROM users WHERE name = ?",
            (name,)
        ).fetchone()
        return User(*row) if row else None

    def update_user(self, id, name=None, email=None, hashed_password=None):
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
        
        self._update_user(user)
        logging.info(f"User {id} updated")

    def delete_user(self, id):
        with self.conn:
            self._delete_user_data(id)
        logging.info(f"User {id} and all related data deleted")

    # Helper methods
    def _fetch_user(self, id):
        return self.conn.execute(
            "SELECT id, name, email, hashed_password FROM users WHERE id = ?", 
            (id,)
        ).fetchone()

    def _update_user(self, user):
        self.conn.execute(
            "UPDATE users SET name = ?, email = ?, hashed_password = ? WHERE id = ?", 
            (user.name, user.email, user.hashed_password, user.id)
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
