import pytest
import subprocess
import os
from finance.database import Database

@pytest.fixture
def db():
    os.environ['DB_NAME'] = 'test_finance.db'
    db = Database('test_finance.db')
    yield db
    db.conn.close()
    os.remove('test_finance.db')

def run_cli_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr

def test_add_user(db):
    stdout, stderr = run_cli_command('python cli.py add_user --name "John Doe"')
    assert 'Added user: John Doe' in stdout

def test_add_account(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    stdout, stderr = run_cli_command(f'python cli.py add_account --user_id {user["id"]} --account_name "Checking" --initial_balance 1000.0')
    assert f'Added account: Checking with balance 1000.0 to user {user["id"]}' in stdout

def test_add_inflow(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    stdout, stderr = run_cli_command(f'python cli.py add_inflow --account_id {account["id"]} --amount 200.0 --description "Salary" --category_name "Salary"')
    assert 'Added income: 200.0 - Salary' in stdout

def test_add_outflow(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    stdout, stderr = run_cli_command(f'python cli.py add_outflow --account_id {account["id"]} --amount 50.0 --description "Groceries" --category_name "Groceries"')
    assert 'Added expense: 50.0 - Groceries' in stdout

def test_generate_report(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    db.add_transaction(user['id'], '2024-05-21', 1500, 'Income', 'Salary', 'Income')
    db.add_transaction(user['id'], '2024-05-22', -200, 'Expense', 'Groceries', 'Expense')
    
    stdout, stderr = run_cli_command(f'python cli.py generate_report --user_id {user["id"]}')
    
    # Check that key parts of the report are present in the output
    assert 'Summary' in stdout
    assert 'Total Balance' in stdout
    assert 'Budget Report for John Doe' in stdout
    assert 'Balance Sheet for John Doe' in stdout
    assert 'Cash Flow Report' in stdout

