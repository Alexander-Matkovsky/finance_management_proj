import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from finance.account import Account
from app.models.database import AccountOperations

class TestAccountOperations(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock(sqlite3.Connection)
        self.account_operations = AccountOperations(self.conn)

    @patch('finance.account.Account.validate')
    def test_add_account(self, mock_validate):
        self.account_operations.add_account(1, 'Savings', 1000)
        self.conn.execute.assert_called_with(
            'INSERT INTO accounts (user_id, name, balance) VALUES (?, ?, ?)',
            (1, 'Savings', 1000)
        )

    def test_get_account(self):
        mock_account_data = (1, 1, 'Savings', 1000)
        self.conn.execute.return_value.fetchone.return_value = mock_account_data
        account = self.account_operations.get_account(1)
        self.assertEqual(account.account_id, 1)
        self.assertEqual(account.user_id, 1)
        self.assertEqual(account.name, 'Savings')
        self.assertEqual(account.balance, 1000)

    def test_get_accounts(self):
        mock_accounts_data = [
            (1, 1, 'Savings', 1000),
            (2, 1, 'Checking', 2000)
        ]
        self.conn.execute.return_value.fetchall.return_value = mock_accounts_data
        accounts = self.account_operations.get_accounts(1)
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0].name, 'Savings')
        self.assertEqual(accounts[1].name, 'Checking')

    @patch('finance.account.Account.validate')
    def test_update_account(self, mock_validate):
        mock_account = Account(1, 1, 'Savings', 1000)
        self.conn.execute.return_value.fetchone.return_value = (1, 1, 'Savings', 1000)
        self.account_operations.update_account(1, 'New Savings', 1500)
        self.conn.execute.assert_called_with(
            "UPDATE accounts SET name = ?, balance = ? WHERE id = ?",
            ('New Savings', 1500, 1)
        )
        self.conn.commit.assert_called_once()

    def test_delete_account(self):
        self.account_operations.delete_account(1)
        self.conn.execute.assert_any_call("DELETE FROM accounts WHERE id = ?", (1,))
        self.conn.execute.assert_any_call("DELETE FROM transactions WHERE account_id = ?", (1,))

if __name__ == '__main__':
    unittest.main()
