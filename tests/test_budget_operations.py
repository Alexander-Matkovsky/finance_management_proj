import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from app.models.database import BudgetOperations

class TestBudgetOperations(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock(sqlite3.Connection)
        self.budget_operations = BudgetOperations(self.conn)

    @patch('finance.budget.Budget.validate')
    def test_set_budget_new(self, mock_validate):
        self.conn.execute.return_value.fetchone.return_value = None
        self.budget_operations.set_budget(1, 'Food', 500)
        self.conn.execute.assert_called_with(
            'INSERT INTO budgets (user_id, category_name, amount, amount_used) VALUES (?, ?, ?, ?)',
            (1, 'Food', 500, 0)
        )

    @patch('finance.budget.Budget.validate')
    def test_set_budget_existing(self, mock_validate):
        existing_budget_data = (1, 1, 'Food', 300, 100)
        self.conn.execute.return_value.fetchone.return_value = existing_budget_data
        self.budget_operations.set_budget(1, 'Food', 500)
        self.conn.execute.assert_called_with(
            'UPDATE budgets SET amount = ? WHERE id = ?',
            (500, 1)
        )

    def test_get_budget(self):
        budget_data = (1, 1, 'Food', 500, 100)
        self.conn.execute.return_value.fetchone.return_value = budget_data
        amount, amount_used = self.budget_operations.get_budget(1, 'Food')
        self.assertEqual(amount, 500)
        self.assertEqual(amount_used, 100)

    def test_get_budgets(self):
        budgets_data = [
            (1, 1, 'Food', 500, 100),
            (2, 1, 'Transport', 300, 50)
        ]
        self.conn.execute.return_value.fetchall.return_value = budgets_data
        budgets = self.budget_operations.get_budgets(1)
        self.assertEqual(len(budgets), 2)
        self.assertEqual(budgets[0].category_name, 'Food')
        self.assertEqual(budgets[1].category_name, 'Transport')

    @patch('finance.budget.Budget.validate')
    def test_update_budget(self, mock_validate):
        budget_data = (1, 1, 'Food', 500, 100)
        self.conn.execute.return_value.fetchone.return_value = budget_data
        self.budget_operations.update_budget(1, 'Food', 700)
        self.conn.execute.assert_called_with(
            "UPDATE budgets SET amount = ? WHERE id = ?",
            (700, 1)
        )
        self.conn.commit.assert_called_once()

    def test_delete_budget(self):
        self.budget_operations.delete_budget(1, 'Food')
        self.conn.execute.assert_called_with(
            "DELETE FROM budgets WHERE user_id = ? AND category_name = ?",
            (1, 'Food')
        )
        self.conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
