import pytest
import subprocess
from finance.database import Database

@pytest.fixture
def db():
    db = Database('test_finance.db')
    yield db
    db.conn.close()
    import os
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
    assert 'Added inflow: 200.0 - Salary' in stdout

def test_add_outflow(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    stdout, stderr = run_cli_command(f'python cli.py add_outflow --account_id {account["id"]} --amount 50.0 --description "Groceries" --category_name "Groceries"')
    assert 'Added outflow: 50.0 - Groceries' in stdout

def test_generate_report(db):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    stdout, stderr = run_cli_command(f'python cli.py generate_report --user_id {user["id"]}')
    assert 'Generated report for user' in stdout
