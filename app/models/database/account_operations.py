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

    def get_account(self, account_id):
        row = self.conn.execute(
            "SELECT id, user_id, name, balance FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
        return Account(*row) if row else None

    def get_accounts(self, user_id):
        rows = self.conn.execute(
            "SELECT id, user_id, name, balance FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchall()
        return [Account(*row) for row in rows] if rows else None

    def update_account(self, account_id, account_name, balance):
        account = self.get_account(account_id)
        if account:
            account.name = account_name
            account.balance = balance
            account.validate()
            self.conn.execute(
                "UPDATE accounts SET name = ?, balance = ? WHERE id = ?",
                (account.name, account.balance, account_id)
            )
            self.conn.commit()
            logging.info(f"Account {account_id} updated to name: {account_name} with balance: {balance}")

    def delete_account(self, account_id):
        with self.conn:
            self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            self.conn.execute("DELETE FROM transactions WHERE account_id = ?", (account_id,))
        logging.info(f"Account {account_id} and all related transactions deleted")

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
