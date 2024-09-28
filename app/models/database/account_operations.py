import logging
import sqlite3
from finance.account import Account

class AccountOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_account(self, user_id, name, balance):
        account = Account(None, user_id, name, balance)
        account.validate()
        self._execute_query(
            'INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)',
            (account.user_id, account.name, account.balance)
        )
        logging.info(f"Account added for user {user_id}: {name} with balance {balance}")

    def get_account(self, id):
        query = "SELECT id, user_id, name, balance FROM accounts WHERE id = ?"
        row = self.conn.execute(query, (id,)).fetchone()
        return Account(*row) if row else None

    def get_user_accounts(self, user_id):  # Changed method name from get_accounts to get_user_accounts
        query = "SELECT id, user_id, name, balance FROM accounts WHERE user_id = ?"
        rows = self.conn.execute(query, (user_id,)).fetchall()
        return [Account(*row) for row in rows] if rows else []

    def update_account(self, id, account_name, balance):
        account = self.get_account(id)
        if account:
            account.name = account_name
            account.balance = balance
            account.validate()
            query = "UPDATE accounts SET name = ?, balance = ? WHERE id = ?"
            params = (account.name, account.balance, id)
            try:
                with self.conn:
                    self.conn.execute(query, params)
                    self.conn.commit()
                logging.info(f"Account {id} updated to name: {account_name} with balance: {balance}")
            except sqlite3.Error as e:
                logging.error(f"Error updating account: {e}")
                raise

    def delete_account(self, id):
        with self.conn:
            self.conn.execute("DELETE FROM accounts WHERE id = ?", (id,))
            self.conn.execute("DELETE FROM transactions WHERE id = ?", (id,))
        logging.info(f"Account {id} and all related transactions deleted")

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