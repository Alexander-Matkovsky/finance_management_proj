import sqlite3


class Database:
    def __init__(self, db_name='finance.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

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
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')

    def add_user(self, name):
        if not name:
            raise ValueError("User name cannot be empty")
        with self.conn:
            self.conn.execute('INSERT INTO users (name) VALUES (?)', (name,))

    def add_account(self, user_id, name, balance):
        if not name:
            raise ValueError("Account name cannot be empty")
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")
        with self.conn:
            self.conn.execute('INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)', (user_id, name, balance))

    def add_transaction(self, account_id, date, amount, type, description):
        if not description:
            raise ValueError("Description cannot be empty")
        if type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description) VALUES (?, ?, ?, ?, ?)', (account_id, date, amount, type, description))

    def add_category(self, name):
        if not name:
            raise ValueError("Category name cannot be empty")
        with self.conn:
            self.conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))

    def add_transaction(self, account_id, date, amount, type, description, category_id):
        if not description:
            raise ValueError("Description cannot be empty")
        if type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description, category_id) VALUES (?, ?, ?, ?, ?, ?)', (account_id, date, amount, type, description, category_id))

# Example usage
if __name__ == "__main__":
    db = Database()
    try:
        db.add_category('Food')
        db.add_user('John Doe')
        db.add_account(1, 'Checking Account', 1000.0)
        db.add_transaction(1, '2023-05-20', 500.0, 'Income', 'Salary', 1)
    except ValueError as e:
        print(f"Error: {e}")