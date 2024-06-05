import pytest
import sqlite3
from app.models.database import Database

@pytest.fixture
def db():
    db = Database('test_finance.db')
    yield db
    db.conn.close()
    import os
    os.remove('test_finance.db')

def test_add_user(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    assert user is not None
    assert user['name'] == 'John Doe'

def test_add_account(db):
    db.add_user('Jane Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('Jane Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    assert account is not None
    assert account['name'] == 'Checking'
    assert account['balance'] == 1000.0

def test_add_transaction(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Savings', 500.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    db.add_transaction(account['id'], '2024-05-27', 200.0, 'Income', 'Salary', 'Salary')
    transaction = db.conn.execute('SELECT * FROM transactions WHERE account_id = ?', (account['id'],)).fetchone()
    assert transaction is not None
    assert transaction['amount'] == 200.0
    assert transaction['description'] == 'Salary'
    assert transaction['category_name'] == 'Salary'

def test_set_budget(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.set_budget(user['id'], 'Groceries', 500.0)
    budget = db.conn.execute('SELECT * FROM budgets WHERE user_id = ? AND category_name = ?', (user['id'], 'Groceries')).fetchone()
    assert budget is not None
    assert budget['amount'] == 500.0

def test_update_user(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.update_user(user['id'], 'Johnny Doe')
    updated_user = db.conn.execute('SELECT * FROM users WHERE id = ?', (user['id'],)).fetchone()
    assert updated_user['name'] == 'Johnny Doe'

def test_update_account(db):
    db.add_user('Jane Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('Jane Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    db.update_account(account['id'], 'Updated Checking', 2000.0)
    updated_account = db.conn.execute('SELECT * FROM accounts WHERE id = ?', (account['id'],)).fetchone()
    assert updated_account['name'] == 'Updated Checking'
    assert updated_account['balance'] == 2000.0

def test_update_transaction(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Savings', 500.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    db.add_transaction(account['id'], '2024-05-27', 200.0, 'Income', 'Salary', 'Salary')
    transaction = db.conn.execute('SELECT * FROM transactions WHERE account_id = ?', (account['id'],)).fetchone()
    db.update_transaction(transaction['id'],'2024-05-27', 300.0, 'Income', 'Bonus', 'Bonus')
    updated_transaction = db.conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction['id'],)).fetchone()
    assert updated_transaction['amount'] == 300.0
    assert updated_transaction['description'] == 'Bonus'
    assert updated_transaction['category_name'] == 'Bonus'
