import logging
import sqlite3

class BudgetOperations:
    def __init__(self, conn):
        self.conn = conn

    def set_budget(self, user_id, category_name, amount):
        try:
            existing_budget = self.conn.execute(
                'SELECT id FROM budgets WHERE user_id = ? AND category_name = ?', 
                (user_id, category_name)
            ).fetchone()
            
            if existing_budget:
                logging.info(f"Updating existing budget for user {user_id}, category {category_name}")
                self.conn.execute(
                    'UPDATE budgets SET amount = ?, category_name = ? WHERE user_id = ? AND category_name = ?', 
                    (amount, category_name, user_id, category_name)
                )
                logging.info(f"Budget updated for user {user_id}, category {category_name}: {amount}")
            else:
                logging.info(f"Inserting new budget for user {user_id}, category {category_name}")
                self.conn.execute(
                    'INSERT INTO budgets (user_id, category_name, amount) VALUES (?, ?, ?)', 
                    (user_id, category_name, amount)
                )
                logging.info(f"Budget set for user {user_id}, category {category_name}: {amount}")
        except sqlite3.Error as e:
            logging.error(f"SQLite error: {e}")
            raise
        except Exception as e:
            logging.error(f"Error setting budget: {e}")
            raise            
        self.conn.commit()  # Commit the transaction to save changes

    def get_budget(self, user_id, category_name):
        budget = self.conn.execute('SELECT amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', (user_id, category_name)).fetchone()
        if budget:
            logging.info(f"Budget retrieved for user {user_id}, category {category_name}: {budget['amount']}, used: {budget['amount_used']}")
            return budget['amount'], budget['amount_used']
        logging.info(f"No budget found for user {user_id}, category {category_name}")
        return None, None

    def update_budget(self, user_id, category_name, new_amount):
        self.conn.execute("UPDATE budgets SET amount = ? WHERE user_id = ? AND category_name = ?", (new_amount, user_id, category_name))
        self.conn.commit()
        logging.info(f"Budget for user {user_id}, category {category_name} updated to {new_amount}")

    def delete_budget(self, user_id, category_name):
        self.conn.execute("DELETE FROM budgets WHERE user_id = ? AND category_name = ?", (user_id, category_name))
        logging.info(f"Budget for user {user_id} and category {category_name} deleted")
