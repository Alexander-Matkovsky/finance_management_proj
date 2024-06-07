import logging
import sqlite3

class TransactionOperations:
    def __init__(self, conn):
        self.conn = conn

    def add_transaction(self, account_id, date, amount, type, description, category_name):
        if not description:
            raise ValueError("Description cannot be empty")
        if type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")
        with self.conn:
            self.conn.execute('INSERT INTO transactions (account_id, date, amount, type, description, category_name) VALUES (?, ?, ?, ?, ?, ?)', (account_id, date, amount, type, description, category_name))
            if type == "Income":
                self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
            else:
                self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (abs(amount), account_id))
                budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (account_id, category_name)).fetchone()
                if budget:
                    new_amount_used = budget["amount_used"] + -amount
                    self.conn.execute('UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (new_amount_used, account_id, category_name))
                    if new_amount_used > budget["amount"]:
                        logging.warning(f"Budget exceeded for user {account_id}, category {category_name}")
        logging.info(f"Transaction added for account {account_id}: {type} of {amount} - {description}")

    def update_transaction(self, transaction_id, date, amount, type, description, category_name):
        self.conn.execute("UPDATE transactions SET amount = ?, description = ?, category_name = ?, date = ?, type = ? WHERE id = ?", (amount, description, category_name, date, type, transaction_id))
        self.conn.commit()
        logging.info(f"Transaction {transaction_id} updated with amount: {amount}, description: {description}, category name: {category_name}, date: {date}, type:{type}")

    def delete_transaction(self, transaction_id):
        transaction = self.conn.execute("SELECT account_id, amount, type, category_name FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
        if transaction:
            with self.conn:
                self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                if transaction["type"] == "Income":
                    self.conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                else:
                    self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (transaction["amount"], transaction["account_id"]))
                    budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (transaction["account_id"], transaction["category_name"])).fetchone()
                    if budget:
                        new_amount_used = budget["amount_used"] - transaction["amount"]
                        self.conn.execute('UPDATE budgets SET amount_used = ? WHERE user_id = (SELECT user_id FROM accounts WHERE id = ?) AND category_name = ?', (new_amount_used, transaction["account_id"], transaction["category_name"]))
            logging.info(f"Transaction {transaction_id} deleted and account balance updated")

    def get_transactions(self, account_id):
        return self.conn.execute("SELECT amount, description, date, category_name FROM transactions WHERE account_id = ?", (account_id,)).fetchall()

    def get_transaction(self, transaction_id):
        return self.conn.execute("SELECT amount, description, date, category_name FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
