import unittest
from finance.account import Account
from finance.transaction import Transaction

class TestAccount(unittest.TestCase):
    def test_add_transaction(self):
        account = Account(1, "Checking Account", 1000)
        transaction = Transaction(1, "2023-05-20", 500, "Income", "Salary")
        account.add_transaction(transaction)
        self.assertEqual(account.get_balance(), 1500)
        self.assertEqual(len(account.get_transactions()), 1)

if __name__ == '__main__':
    unittest.main()
