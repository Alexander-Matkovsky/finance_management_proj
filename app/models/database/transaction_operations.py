import logging
from finance.transaction import Transaction
from datetime import datetime

class TransactionOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_transaction(self, account_id, date, amount, type, description, category_name):
        transaction = Transaction(account_id, date, amount, type, description, category_name)
        
        with self.conn:
            transaction_id = self._insert_transaction(transaction)
            self._update_account_balance(transaction)
            self._update_budget(transaction)
        
        logging.info(f"Transaction added for account {transaction.account_id}: {transaction.type} of {transaction.amount} - {transaction.description}")
        return transaction_id

    def update_transaction(self, transaction_id, date, amount, type, description, category_name):
        transaction = Transaction(None, date, amount, type, description, category_name)
        self._execute_update_transaction(transaction_id, transaction)
        logging.info(f"Transaction {transaction_id} updated: {amount} - {description}")

    def delete_transaction(self, transaction_id):
        transaction = self._get_transaction_details(transaction_id)
        if transaction:
            with self.conn:
                self._delete_transaction_record(transaction_id)
                self._revert_account_balance(transaction)
                self._revert_budget(transaction)
            logging.info(f"Transaction {transaction_id} deleted and account balance updated")

    def get_transactions(self, account_ids=None, start_date=None, end_date=None, transaction_type=None, category=None):
        query = """
            SELECT id, account_id, date, amount, type, description, category_name 
            FROM transactions 
            WHERE 1=1
        """
        params = []

        if account_ids:
            query += " AND account_id IN ({})".format(','.join(['?']*len(account_ids)))
            params.extend(account_ids)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)
        
        if category:
            query += " AND category_name = ?"
            params.append(category)

        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_transaction(self, transaction_id):
        row = self.conn.execute(
            "SELECT id, account_id, date, amount, type, description, category_name FROM transactions WHERE id = ?", 
            (transaction_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    # Helper methods
    def _insert_transaction(self, transaction):
        cursor = self.conn.execute(
            'INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)', 
            (transaction.account_id, transaction.date, transaction.amount, transaction.type, transaction.description, transaction.category_name)
        )
        return cursor.lastrowid

    def _update_account_balance(self, transaction):
        if transaction.type == "Income":
            self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction.amount, transaction.account_id))
        else:
            self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (abs(transaction.amount), transaction.account_id))

    def _update_budget(self, transaction):
        if transaction.type != "Income":
            budget = self._get_budget(transaction.account_id, transaction.category_name)
            if budget:
                new_amount_used = budget["amount_used"] + abs(transaction.amount)
                self._update_budget_amount_used(transaction.account_id, transaction.category_name, new_amount_used)
                if new_amount_used > budget["amount"]:
                    logging.warning(f"Budget exceeded for user {transaction.account_id}, category {transaction.category_name}")

    def _get_budget(self, account_id, category_name):
        row = self.conn.execute(
            'SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
            (account_id, category_name)
        ).fetchone()
        return dict(row) if row else None

    def _update_budget_amount_used(self, account_id, category_name, new_amount_used):
        self.conn.execute(
            'UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
            (new_amount_used, account_id, category_name)
        )

    def _execute_update_transaction(self, transaction_id, transaction):
        self.conn.execute(
            "UPDATE transactions SET amount = ?, description = ?, category_name = ?, date = ?, type = ? WHERE id = ?", 
            (transaction.amount, transaction.description, transaction.category_name, transaction.date, transaction.type, transaction_id)
        )
        self.conn.commit()

    def _get_transaction_details(self, transaction_id):
        row = self.conn.execute(
            "SELECT id, account_id, date, amount, type, description, category_name FROM transactions WHERE id = ?", 
            (transaction_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    def _delete_transaction_record(self, transaction_id):
        self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))

    def _revert_account_balance(self, transaction):
        if transaction["type"] == "Income":
            self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
        else:
            self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))

    def _revert_budget(self, transaction):
        if transaction["type"] != "Income":
            budget = self._get_budget(transaction["account_id"], transaction["category_name"])
            if budget:
                new_amount_used = budget["amount_used"] - transaction["amount"]
                self._update_budget_amount_used(transaction["account_id"], transaction["category_name"], new_amount_used)

    def _row_to_dict(self, row):
        if row:
            return {
                "id": row[0],
                "account_id": row[1],
                "date": row[2],
                "amount": row[3],
                "type": row[4],
                "description": row[5],
                "category_name": row[6]
            }
        return None