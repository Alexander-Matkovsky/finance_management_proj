import sqlite3
import logging
import os

class Database:
    def __init__(self, db_name=None):
        self.db_name = os.getenv("DB_NAME", 'finance.db')
        self.conn = self.get_connection()
        self.create_tables()
        logging.info("Database connected")

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        table_creation_queries = [
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                balance REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, name)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                category_name TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_name TEXT NOT NULL,
                amount REAL NOT NULL,
                amount_used REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, category_name)
            )
            '''
        ]
        with self.conn:
            for query in table_creation_queries:
                self.conn.execute(query)
        logging.info("Tables created or verified")

    def execute_query(self, query, params=()):
        try:
            with self.conn:
                self.conn.execute(query, params)
        except sqlite3.IntegrityError as e:
            logging.error(f"IntegrityError: {e}")
            raise
        except sqlite3.OperationalError as e:
            logging.error(f"OperationalError: {e}")
            raise

    def add_user(self, name):
        """Add a new user to the database."""
        if not name:
            raise ValueError("User name cannot be empty")
        self.execute_query('INSERT INTO users (name) VALUES (?)', (name,))
        logging.info(f"User added: {name}")

    def add_account(self, user_id, name, balance):
        """Add a new account for a user."""
        if not name:
            raise ValueError("Account name cannot be empty")
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self.execute_query('INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)', (user_id, name, balance))
        logging.info(f"Account added for user {user_id}: {name} with balance {balance}")

    def add_transaction(self, account_id, date, amount, type, description, category_name):
        """Add a new transaction for an account."""
        if not description:
            raise ValueError("Description cannot be empty")
        if type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)', (account_id, date, amount, type, description, category_name))
            if type == "Income":
                self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
            else:
                self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (abs(amount), account_id))
                budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (account_id, category_name)).fetchone()
                if budget:
                    new_amount_used = budget["amount_used"] + abs(amount)
                    self.conn.execute('UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (new_amount_used, account_id, category_name))
                    if new_amount_used > budget["amount"]:
                        logging.warning(f"Budget exceeded for user {account_id}, category {category_name}")
        logging.info(f"Transaction added for account {account_id}: {type} of {amount} - {description}")

    def set_budget(self, user_id, category_name, amount):
        """Set or update a budget for a user."""
        existing_budget = self.conn.execute('SELECT id FROM budgets WHERE user_id = ? AND category_name = ?', (user_id, category_name)).fetchone()
        if existing_budget:
            self.conn.execute('UPDATE budgets SET amount = ? WHERE user_id = ? AND category_name = ?', (amount, user_id, category_name))
            logging.info(f"Budget updated for user {user_id}, category {category_name}: {amount}")
        else:
            self.conn.execute('INSERT INTO budgets (user_id, category_name, amount) VALUES (?, ?, ?)', (user_id, category_name, amount))
            logging.info(f"Budget set for user {user_id}, category {category_name}: {amount}")

    def get_budget(self, user_id, category_name):
        """Retrieve the budget and amount used for a category."""
        budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', (user_id, category_name)).fetchone()
        if budget:
            logging.info(f"Budget retrieved for user {user_id}, category {category_name}: {budget['amount']}, used: {budget['amount_used']}")
            return budget['amount'], budget['amount_used']
        logging.info(f"No budget found for user {user_id}, category {category_name}")
        return None, None

    def update_user(self, user_id, name):
        """Update the name of a user."""
        self.conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
        self.conn.commit()
        logging.info(f"User {user_id} updated to name: {name}")

    def update_account(self, account_id, account_name, initial_balance):
        """Update the name and balance of an account."""
        self.conn.execute("UPDATE accounts SET name = ?, balance = ? WHERE id = ?", (account_name, initial_balance, account_id))
        self.conn.commit()
        logging.info(f"Account {account_id} updated to name: {account_name} with balance: {initial_balance}")

    def update_transaction(self, transaction_id, amount, description, category_name):
        """Update the details of a transaction."""
        self.conn.execute("UPDATE transactions SET amount = ?, description = ?, category_name = ? WHERE id = ?", (amount, description, category_name, transaction_id))
        self.conn.commit()
        logging.info(f"Transaction {transaction_id} updated with amount: {amount}, description: {description}, category name: {category_name}")

    def delete_user(self, user_id):
        """Delete a user and all related data."""
        with self.conn:
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM transactions WHERE account_id IN (SELECT id FROM accounts WHERE user_id = ?)", (user_id,))
        logging.info(f"User {user_id} and all related data deleted")

    def delete_account(self, account_id):
        """Delete an account and all related transactions."""
        with self.conn:
            self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            self.conn.execute("DELETE FROM transactions WHERE account_id = ?", (account_id,))
        logging.info(f"Account {account_id} and all related transactions deleted")

    def delete_transaction(self, transaction_id):
        """Delete a transaction and update the account balance and budget usage."""
        transaction = self.conn.execute("SELECT account_id, amount, type, category_name FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
        if transaction:
            with self.conn:
                self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                if transaction["type"] == "Income":
                    self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                else:
                    self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                    budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (transaction["account_id"], transaction["category_name"])).fetchone()
                    if budget:
                        new_amount_used = budget["amount_used"] - transaction["amount"]
                        self.conn.execute('UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (new_amount_used, transaction["account_id"], transaction["category_name"]))
            logging.info(f"Transaction {transaction_id} deleted and account balance updated")

    def delete_budget(self, user_id, category_name):
        """Delete a budget."""
        self.conn.execute("DELETE FROM budgets WHERE user_id = ? AND category_name = ?", (user_id, category_name))
        logging.info(f"Budget for user {user_id} and category {category_name} deleted")

    # New methods for fetching users, accounts, and transactions
    def get_users(self):
        return self.conn.execute("SELECT * FROM users").fetchall()

    def get_accounts(self):
        return self.conn.execute("SELECT * FROM accounts").fetchall()

    def get_transactions_by_user(self, user_id):
        return self.conn.execute("""
            SELECT t.* FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = ?
        """, (user_id,)).fetchall()

    def get_transactions_by_account(self, account_id):
        return self.conn.execute("SELECT * FROM transactions WHERE account_id = ?", (account_id,)).fetchall()

    def get_transactions_by_category(self, category_name):
        return self.conn.execute("SELECT * FROM transactions WHERE category_name = ?", (category_name,)).fetchall()

    def get_transactions_by_date(self, start_date, end_date):
        return self.conn.execute("SELECT * FROM transactions WHERE date BETWEEN ? AND ?", (start_date, end_date)).fetchall()

    def get_transactions_by_type(self, type):
        return self.conn.execute("SELECT * FROM transactions WHERE type = ?", (type,)).fetchall()

    def get_transactions_by_description(self, description):
        return self.conn.execute("SELECT * FROM transactions WHERE description = ?", (description,)).fetchall()

    def get_transactions_by_category_and_type(self, category_name, type):
        return self.conn.execute("SELECT * FROM transactions WHERE category_name = ? AND type = ?", (category_name, type)).fetchall()
