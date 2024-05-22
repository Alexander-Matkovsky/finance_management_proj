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
        with self.conn:
            self.conn.execute('INSERT INTO users (name) VALUES (?)', (name,))

    def add_account(self, user_id, name, balance):
        with self.conn:
            self.conn.execute('INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)', (user_id, name, balance))

    def add_transaction(self, account_id, date, amount, type, description):
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description) VALUES (?, ?, ?, ?, ?)', (account_id, date, amount, type, description))

# Example usage
if __name__ == "__main__":
    db = Database()
    db.add_user('John Doe')
    db.add_account(1, 'Checking Account', 1000.0)
    db.add_transaction(1, '2023-05-20', 500.0, 'Income', 'Salary')
