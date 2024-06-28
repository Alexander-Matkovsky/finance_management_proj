import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from app.models.database import TransactionOperations

class TestTransactionOperations(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock(sqlite3.Connection)
        self.transaction_operations = TransactionOperations(self.conn)

    @patch('finance.transaction.Transaction')
    def test_add_transaction_income(self, MockTransaction):
        mock_transaction = MockTransaction.return_value
        mock_transaction.type = 'Income'
        mock_transaction.amount = 1000
        
        self.transaction_operations.add_transaction(1, '2024-06-28', 1000, 'Income', 'Salary', 'Income')
        
        self.conn.execute.assert_any_call(
            'INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)',
            (1, '2024-06-28', 1000, 'Income', 'Salary', 'Income')
        )
        self.conn.execute.assert_any_call(
            'UPDATE accounts SET balance = balance + ? WHERE id = ?',
            (1000, 1)
        )

    @patch('finance.transaction.Transaction')
    def test_add_transaction_expense(self, MockTransaction):
        mock_transaction = MockTransaction.return_value
        mock_transaction.type = 'Expense'
        mock_transaction.amount = 100
        mock_budget = {'amount': 500, 'amount_used': 200}
        self.conn.execute.return_value.fetchone.side_effect = [mock_budget]

        self.transaction_operations.add_transaction(1, '2024-06-28', 100, 'Expense', 'Groceries', 'Food')

        self.conn.execute.assert_any_call(
            'INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)',
            (1, '2024-06-28', 100, 'Expense', 'Groceries', 'Food')
        )
        self.conn.execute.assert_any_call(
            'UPDATE accounts SET balance = balance - ? WHERE id = ?',
            (100, 1)
        )
        self.conn.execute.assert_any_call(
            'UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?',
            (300, 1, 'Food')
        )

    @patch('finance.transaction.Transaction')
    def test_update_transaction(self, MockTransaction):
        self.transaction_operations.update_transaction(1, '2024-06-28', 500, 'Income', 'Updated Salary', 'Income')

        self.conn.execute.assert_called_with(
            "UPDATE transactions SET amount = ?, description = ?, category_name = ?, date = ?, type = ? WHERE id = ?",
            (500, 'Updated Salary', 'Income', '2024-06-28', 'Income', 1)
        )
        self.conn.commit.assert_called_once()

    def test_delete_transaction_income(self):
        mock_transaction = {'account_id': 1, 'amount': 500, 'type': 'Income', 'category_name': 'Income'}
        self.conn.execute.return_value.fetchone.return_value = mock_transaction

        self.transaction_operations.delete_transaction(1)

        self.conn.execute.assert_any_call("DELETE FROM transactions WHERE id = ?", (1,))
        self.conn.execute.assert_any_call('UPDATE accounts SET balance = balance - ? WHERE id = ?', (500, 1))

    def test_delete_transaction_expense(self):
        mock_transaction = {'account_id': 1, 'amount': 100, 'type': 'Expense', 'category_name': 'Food'}
        mock_budget = {'amount': 500, 'amount_used': 200}
        self.conn.execute.return_value.fetchone.side_effect = [mock_transaction, mock_budget]

        self.transaction_operations.delete_transaction(1)

        self.conn.execute.assert_any_call("DELETE FROM transactions WHERE id = ?", (1,))
        self.conn.execute.assert_any_call('UPDATE accounts SET balance = balance + ? WHERE id = ?', (100, 1))
        self.conn.execute.assert_any_call(
            'UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?',
            (100, 1, 'Food')
        )

    def test_get_transactions(self):
        transactions_data = [
            {'amount': 500, 'description': 'Salary', 'date': '2024-06-28', 'category_name': 'Income'},
            {'amount': 100, 'description': 'Groceries', 'date': '2024-06-28', 'category_name': 'Food'}
        ]
        self.conn.execute.return_value.fetchall.return_value = transactions_data
        
        transactions = self.transaction_operations.get_transactions(1)
        
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['amount'], 500)
        self.assertEqual(transactions[1]['amount'], 100)

    def test_get_transaction(self):
        transaction_data = {'amount': 500, 'description': 'Salary', 'date': '2024-06-28', 'category_name': 'Income'}
        self.conn.execute.return_value.fetchone.return_value = transaction_data
        
        transaction = self.transaction_operations.get_transaction(1)
        
        self.assertEqual(transaction['amount'], 500)
        self.assertEqual(transaction['description'], 'Salary')

if __name__ == '__main__':
    unittest.main()
