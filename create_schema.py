import sqlite3

def create_schema():
    connection = sqlite3.connect('finance.db')
    cursor = connection.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    # Create Accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        balance REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create Transactions table
    cursor.execute('''
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

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_schema()
