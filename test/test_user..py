import unittest
from finance.user import User
from finance.account import Account
from finance.budget import Budget

class TestUser(unittest.TestCase):
    def test_add_account(self):
        user = User(1, "Alice")
        account = Account(1, "Checking Account", 1000)
        user.add_account(account)
        self.assertEqual(len(user.accounts), 1)
        self.assertEqual(user.accounts[0].account_name, "Checking Account")

    def test_add_budget(self):
        user = User(1, "Alice")
        budget = Budget(1, "Groceries", 500)
        user.add_budget(budget)
        self.assertEqual(len(user.budgets), 1)
        self.assertEqual(user.budgets[0].category, "Groceries")

    def test_get_total_balance(self):
        user = User(1, "Alice")
        account1 = Account(1, "Checking Account", 1000)
        account2 = Account(2, "Savings Account", 2000)
        user.add_account(account1)
        user.add_account(account2)
        self.assertEqual(user.get_total_balance(), 3000)

    def test_generate_financial_report(self):
        user = User(1, "Alice")
        account = Account(1, "Checking Account", 1000)
        user.add_account(account)
        report = user.generate_financial_report()
        expected_report = ("Financial Report for Alice\n"
                           "Total Balance: 1000\n"
                           "Account Checking Account: 1000\n")
        self.assertEqual(report, expected_report)

if __name__ == '__main__':
    unittest.main()
