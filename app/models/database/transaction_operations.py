import logging
from finance.transaction import Transaction

class TransactionOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_transaction(self, account_id, date, amount, type, description, category_name):
        transaction = Transaction(account_id, date, amount, type, description, category_name)
        
        with self.conn:
            self.conn.execute(
                'INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)', 
                (transaction.account_id, transaction.date, transaction.amount, transaction.type, transaction.description, transaction.category_name)
            )
            if transaction.type == "Income":
                self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction.amount, transaction.account_id))
            else:
                self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (abs(transaction.amount), transaction.account_id))
                budget = self.conn.execute(
                    'SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
                    (transaction.account_id, transaction.category_name)
                ).fetchone()
                if budget:
                    new_amount_used = budget["amount_used"] + abs(transaction.amount)
                    self.conn.execute(
                        'UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
                        (new_amount_used, transaction.account_id, transaction.category_name)
                    )
                    if new_amount_used > budget["amount"]:
                        logging.warning(f"Budget exceeded for user {transaction.account_id}, category {transaction.category_name}")
        
        logging.info(f"Transaction added for account {transaction.account_id}: {transaction.type} of {transaction.amount} - {transaction.description}")

    def update_transaction(self, transaction_id, date, amount, type, description, category_name):
        transaction = Transaction(None, date, amount, type, description, category_name)  # No account_id needed for validation
        self.conn.execute(
            "UPDATE transactions SET amount = ?, description = ?, category_name = ?, date = ?, type = ? WHERE id = ?", 
            (transaction.amount, transaction.description, transaction.category_name, transaction.date, transaction.type, transaction_id)
        )
        self.conn.commit()
        logging.info(f"Transaction {transaction_id} updated with amount: {transaction.amount}, description: {transaction.description}, category name: {transaction.category_name}, date: {transaction.date}, type:{transaction.type}")

    def delete_transaction(self, transaction_id):
        transaction = self.conn.execute(
            "SELECT account_id, amount, type, category_name FROM transactions WHERE id = ?", 
            (transaction_id,)
        ).fetchone()
        if transaction:
            with self.conn:
                self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                if transaction["type"] == "Income":
                    self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                else:
                    self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                    budget = self.conn.execute(
                        'SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
                        (transaction["account_id"], transaction["category_name"])
                    ).fetchone()
                    if budget:
                        new_amount_used = budget["amount_used"] - transaction["amount"]
                        self.conn.execute(
                            'UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', 
                            (new_amount_used, transaction["account_id"], transaction["category_name"])
                        )
            logging.info(f"Transaction {transaction_id} deleted and account balance updated")

    def get_transactions(self, account_id):
        rows = self.conn.execute(
            "SELECT amount, description, date, category_name FROM transactions WHERE account_id = ?", 
            (account_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def get_transaction(self, transaction_id):
        return self.conn.execute(
            "SELECT amount, description, date, category_name FROM transactions WHERE id = ?", 
            (transaction_id,)
        ).fetchone()