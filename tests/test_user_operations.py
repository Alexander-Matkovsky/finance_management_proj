import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from app.models.database import UserOperations
class TestUserOperations(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock(sqlite3.Connection)
        self.user_operations = UserOperations(self.conn)

    @patch('finance.user.User')
    def test_add_user(self, MockUser):
        mock_user = MockUser.return_value
        mock_user.name = 'John Doe'
        
        self.user_operations.add_user('John Doe')
        
        self.conn.execute.assert_called_with('INSERT INTO users (name) VALUES (?)', ('John Doe',))

    @patch('finance.user.User')
    def test_get_user(self, MockUser):
        mock_row = (1, 'John Doe')
        self.conn.execute.return_value.fetchone.return_value = mock_row
        mock_user = MockUser.return_value
        
        user = self.user_operations.get_user(1)
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.name, 'John Doe')

    @patch('finance.user.User')
    def test_update_user(self, MockUser):
        mock_user = MockUser.return_value
        mock_user.id = 1
        mock_user.name = 'Jane Doe'
        
        self.user_operations.update_user(1, 'Jane Doe')
        
        self.conn.execute.assert_called_with("UPDATE users SET name = ? WHERE id = ?", ('Jane Doe', 1))
        self.conn.commit.assert_called_once()

    def test_delete_user(self):
        self.user_operations.delete_user(1)
        
        self.conn.execute.assert_any_call("DELETE FROM users WHERE id = ?", (1,))
        self.conn.execute.assert_any_call("DELETE FROM accounts WHERE id = ?", (1,))
        self.conn.execute.assert_any_call("DELETE FROM budgets WHERE id = ?", (1,))
        self.conn.execute.assert_any_call("DELETE FROM transactions WHERE account_id IN (SELECT id FROM accounts WHERE id = ?)", (1,))

if __name__ == '__main__':
    unittest.main()
