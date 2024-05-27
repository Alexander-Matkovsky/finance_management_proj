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
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
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

    def add_transaction(self, account_id, date, amount, type, description, category_name):
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
        logging.info(f"Transaction added for account {account_id}: {type} of {amount} - {description}")

    def set_budget(self, user_id, category_name, amount):
        existing_budget = self.conn.execute('SELECT id FROM budgets WHERE user_id = ? AND category_name = ?', (user_id, category_name)).fetchone()
        if existing_budget:
            self.conn.execute('UPDATE budgets SET amount = ? WHERE user_id = ? AND category_name = ?', (amount, user_id, category_name))
            logging.info(f"Budget updated for user {user_id}, category {category_name}: {amount}")
        else:
            self.conn.execute('INSERT INTO budgets (user_id, category_name, amount) VALUES (?, ?, ?)', (user_id, category_name, amount))
            logging.info(f"Budget set for user {user_id}, category {category_name}: {amount}")

    def get_budget(self, user_id, category_name):
        budget = self.conn.execute('SELECT amount FROM budgets WHERE user_id = ? AND category_name = ?', (user_id, category_name)).fetchone()
        if budget:
            logging.info(f"Budget retrieved for user {user_id}, category {category_name}: {budget[0]}")
            return budget[0]
        logging.info(f"No budget found for user {user_id}, category {category_name}")
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

