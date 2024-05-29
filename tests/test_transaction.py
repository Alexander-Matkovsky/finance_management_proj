import unittest
from finance.transaction import Transaction

class TestTransaction(unittest.TestCase):
    def test_transaction_creation(self):
        transaction = Transaction(1, "2023-05-20", 500, "Income", "Salary")
        self.assertEqual(transaction.transaction_id, 1)
        self.assertEqual(transaction.date, "2023-05-20")
        self.assertEqual(transaction.amount, 500)
        self.assertEqual(transaction.category, "Income")
        self.assertEqual(transaction.description, "Salary")

    def test_transaction_str(self):
        transaction = Transaction(1, "2023-05-20", 500, "Income", "Salary")
        self.assertEqual(str(transaction), "2023-05-20 - Income: 500 (Salary)")

if __name__ == '__main__':
    unittest.main()
