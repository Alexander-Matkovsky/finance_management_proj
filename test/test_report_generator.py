import unittest
from finance.user import User
from finance.account import Account
from finance.transaction import Transaction
from finance.budget import Budget
from finance.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def test_generate_balance_sheet(self):
        user = User(1, "Alice")
        account = Account(1, "Checking Account", 1000)
        user.add_account(account)
        report = ReportGenerator.generate_balance_sheet(user)
        expected_report = "Balance Sheet for Alice\nAccount Checking Account: 1000\n"
        self.assertEqual(report, expected_report)

    def test_generate_income_statement(self):
        user = User(1, "Alice")
        account = Account(1, "Checking Account", 1000)
        transaction = Transaction(1, "2023-05-20", 500, "Income", "Salary")
        account.add_transaction(transaction)
        user.add_account(account)
        report = ReportGenerator.generate_income_statement(user)
        expected_report = "Income Statement for Alice\nIncome: 2023-05-20 - Income: 500 (Salary)\n"
        self.assertEqual(report, expected_report)

    def test_generate_budget_report(self):
        user = User(1, "Alice")
        budget = Budget(1, "Groceries", 500)
        budget.add_expense(200)
        user.add_budget(budget)
        report = ReportGenerator.generate_budget_report(user)
        expected_report = "Budget Report for Alice\nCategory Groceries: Spent 200, Limit 500\n"
        self.assertEqual(report, expected_report)

    def test_generate_cash_flow_statement(self):
        user = User(1, "Alice")
        account = Account(1, "Checking Account", 1000)
        transaction1 = Transaction(1, "2023-05-20", 500, "Income", "Salary")
        transaction2 = Transaction(2, "2023-05-21", -200, "Expense", "Groceries")
        account.add_transaction(transaction1)
        account.add_transaction(transaction2)
        user.add_account(account)
        report = ReportGenerator.generate_cash_flow_statement(user)
        expected_report = ("Cash Flow Report\n"
                           "Inflows:\n"
                           "Salary: 500\n"
                           "Outflows:\n"
                           "Groceries: -200\n"
                           "Net Cash Flow: 300\n")
        self.assertEqual(report, expected_report)

if __name__ == '__main__':
    unittest.main()
