import logging
import sqlite3
from finance.budget import Budget
class BudgetOperations:
    def __init__(self, conn):
        self.conn = conn

    def set_budget(self, user_id, category_name, amount):
        try:
            existing_budget = self.conn.execute(
                'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', 
                (user_id, category_name)
            ).fetchone()
            
            if existing_budget:
                budget = Budget(*existing_budget)
                logging.info(f"Updating existing budget for user {user_id}, category {category_name}")
                budget.amount = amount
                budget.validate()
                self.conn.execute(
                    'UPDATE budgets SET amount = ? WHERE id = ?', 
                    (budget.amount, budget.id)
                )
                logging.info(f"Budget updated for user {user_id}, category {category_name}: {amount}")
            else:
                logging.info(f"Inserting new budget for user {user_id}, category {category_name}")
                budget = Budget(None, user_id, category_name, amount, 0)
                budget.validate()
                self.conn.execute(
                    'INSERT INTO budgets (user_id, category_name, amount, amount_used) VALUES (?, ?, ?, ?)', 
                    (budget.user_id, budget.category_name, budget.amount, budget.amount_used)
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
        budget_row = self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', 
            (user_id, category_name)
        ).fetchone()
        
        if budget_row:
            budget = Budget(*budget_row)
            logging.info(f"Budget retrieved for user {user_id}, category {category_name}: {budget.amount}, used: {budget.amount_used}")
            return budget.amount, budget.amount_used
        logging.info(f"No budget found for user {user_id}, category {category_name}")
        return None, None

    def get_budgets(self, user_id):
        budgets = []
        budget_rows = self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ?',
            (user_id,)
        ).fetchall()
        
        for budget_row in budget_rows:
            budget = Budget(*budget_row)
            budgets.append(budget)  # Remove the asterisk here
        
        logging.info(f"Retrieved {len(budgets)} budgets for user {user_id}")
        return budgets

    def update_budget(self, user_id, category_name, new_amount):
        budget_row = self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?',
            (user_id, category_name)
        ).fetchone()
        
        if budget_row:
            budget = Budget(*budget_row)
            budget.amount = new_amount
            budget.validate()
            self.conn.execute(
                "UPDATE budgets SET amount = ? WHERE id = ?", 
                (budget.amount, budget.id)
            )
            self.conn.commit()
            logging.info(f"Budget for user {user_id}, category {category_name} updated to {new_amount}")

    def delete_budget(self, user_id, category_name):
        self.conn.execute("DELETE FROM budgets WHERE user_id = ? AND category_name = ?", (user_id, category_name))
        self.conn.commit()
        logging.info(f"Budget for user {user_id} and category {category_name} deleted")
