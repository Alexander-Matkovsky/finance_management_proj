import pytest
from finance.database import Database
from finance.report_generator import ReportGenerator

@pytest.fixture
def db():
    db = Database('test_finance.db')
    yield db
    db.conn.close()
    import os
    os.remove('test_finance.db')

@pytest.fixture
def report_generator(db):
    return ReportGenerator(db)

def test_generate_balance_sheet(db, report_generator):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    balance_sheet = report_generator.generate_balance_sheet(user)
    assert 'Balance Sheet for John Doe' in balance_sheet
    assert 'Account Checking: 1000.0' in balance_sheet
    assert 'Total Balance: 1000.0' in balance_sheet

def test_generate_budget_report(db, report_generator):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.set_budget(user['id'], 'Groceries', 500.0)
    budget_report = report_generator.generate_budget_report(user)
    assert 'Budget Report for John Doe' in budget_report
    assert 'Category Groceries: Spent 0, Limit 500.0' in budget_report

def test_generate_cash_flow_statement(db, report_generator):
    db.add_user('John Doe')
    user = db.conn.execute('SELECT * FROM users WHERE name = ?', ('John Doe',)).fetchone()
    db.add_account(user['id'], 'Checking', 1000.0)
    account = db.conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user['id'],)).fetchone()
    db.add_transaction(account['id'], '2024-05-27', 200.0, 'Income', 'Salary', 'Salary')
    db.add_transaction(account['id'], '2024-05-27', -50.0, 'Expense', 'Groceries', 'Groceries')
    cash_flow_statement = report_generator.generate_cash_flow_statement(user)
    assert 'Cash Flow Report' in cash_flow_statement
    assert 'Inflows:\n2024-05-27 - Salary: 200.0' in cash_flow_statement
    assert 'Outflows:\n2024-05-27 - Groceries: -50.0' in cash_flow_statement
    assert 'Net Cash Flow: 150.0' in cash_flow_statement
