import logging
import sqlite3

class AccountOperations:
    def __init__(self, conn):
        self.conn = conn
        

    def add_account(self, user_id, name, balance):
        if not name:
            raise ValueError("Account name cannot be empty")
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._execute_query('INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)', (user_id, name, balance))
        logging.info(f"Account added for user {user_id}: {name} with balance {balance}")

    def get_accounts(self, user_id):
        return self.conn.execute("SELECT id, name, balance FROM accounts WHERE user_id = ?", (user_id,)).fetchall()

    def update_account(self, account_id, account_name, initial_balance):
        self.conn.execute("UPDATE accounts SET name = ?, balance = ? WHERE id = ?", (account_name, initial_balance, account_id))
        self.conn.commit()
        logging.info(f"Account {account_id} updated to name: {account_name} with balance: {initial_balance}")

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
