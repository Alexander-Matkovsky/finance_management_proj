import sqlite3
import logging

class Database:
    def __init__(self, db_name='finance.db'):
        self.db_name = db_name
        self.conn = self.get_connection()  # Initialize the connection here
        self.create_tables()
        logging.info("Database connected")

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    balance REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER,
                    FOREIGN KEY (account_id) REFERENCES accounts (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_id INTEGER,
                    amount REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
        logging.info("Tables created or verified")

    def add_user(self, name):
        if not name:
            raise ValueError("User name cannot be empty")
        with self.conn:
            self.conn.execute('INSERT INTO users (name) VALUES (?)', (name,))
        logging.info(f"User added: {name}")

    def add_account(self, user_id, name, balance):
        if not name:
            raise ValueError("Account name cannot be empty")
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")
        with self.conn:
            self.conn.execute('INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)', (user_id, name, balance))
        logging.info(f"Account added for user {user_id}: {name} with balance {balance}")

    def add_transaction(self, account_id, date, amount, type, description, category_id):
        if not description:
            raise ValueError("Description cannot be empty")
        if type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description, category_id) VALUES (?, ?, ?, ?, ?, ?)', (account_id, date, amount, type, description, category_id))
        logging.info(f"Transaction added for account {account_id}: {type} of {amount} - {description}")

    def add_category(self, name):
        if not name:
            raise ValueError("Category name cannot be empty")
        with self.conn:
            self.conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        logging.info(f"Category added: {name}")

    def set_budget(self, user_id, category_id, amount):
        with self.conn:
            self.conn.execute('INSERT INTO budgets (user_id, category_id, amount) VALUES (?, ?, ?)', (user_id, category_id, amount))
        logging.info(f"Budget set for user {user_id}, category {category_id}: {amount}")

    def get_budget(self, user_id, category_id):
        budget = self.conn.execute('SELECT amount FROM budgets WHERE user_id = ? AND category_id = ?', (user_id, category_id)).fetchone()
        if budget:
            logging.info(f"Budget retrieved for user {user_id}, category {category_id}: {budget[0]}")
            return budget[0]
        logging.info(f"No budget found for user {user_id}, category {category_id}")
        return None

    def update_user(self, user_id, name):
        self.conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
        self.conn.commit()
        logging.info(f"User {user_id} updated to name: {name}")

    def update_account(self, account_id, account_name, initial_balance):
        self.conn.execute("UPDATE accounts SET name = ?, balance = ? WHERE id = ?", (account_name, initial_balance, account_id))
        self.conn.commit()
        logging.info(f"Account {account_id} updated to name: {account_name} with balance: {initial_balance}")

    def update_category(self, category_id, name):
        self.conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))
        self.conn.commit()
        logging.info(f"Category {category_id} updated to name: {name}")

    def update_transaction(self, transaction_id, amount, description, category_id):
        self.conn.execute("UPDATE transactions SET amount = ?, description = ?, category_id = ? WHERE id = ?", (amount, description, category_id, transaction_id))
        self.conn.commit()
        logging.info(f"Transaction {transaction_id} updated with amount: {amount}, description: {description}, category ID: {category_id}")

