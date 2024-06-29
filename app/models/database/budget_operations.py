import logging
import sqlite3
from finance.budget import Budget

class BudgetOperations:
    def __init__(self, conn):
        self.conn = conn

    def set_budget(self, user_id, category_name, amount):
        try:
            existing_budget = self._get_existing_budget(user_id, category_name)
            
            if existing_budget:
                self._update_existing_budget(existing_budget, amount)
            else:
                self._insert_new_budget(user_id, category_name, amount)
            
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"SQLite error: {e}")
            raise
        except Exception as e:
            logging.error(f"Error setting budget: {e}")
            raise

    def get_budget(self, user_id, category_name):
        budget_row = self._fetch_budget_row(user_id, category_name)
        
        if budget_row:
            budget = Budget(*budget_row)
            logging.info(f"Budget retrieved for user {user_id}, category {category_name}: {budget.amount}, used: {budget.amount_used}")
            return budget.amount, budget.amount_used
        
        logging.info(f"No budget found for user {user_id}, category {category_name}")
        return None, None

    def get_budgets(self, user_id):
        budget_rows = self._fetch_all_budget_rows(user_id)
        budgets = [Budget(*row) for row in budget_rows]
        
        logging.info(f"Retrieved {len(budgets)} budgets for user {user_id}")
        return budgets

    def update_budget(self, user_id, category_name, new_amount):
        budget_row = self._fetch_budget_row(user_id, category_name)
        
        if budget_row:
            budget = Budget(*budget_row)
            budget.amount = new_amount
            budget.validate()
            self._execute_update_budget(budget)
            logging.info(f"Budget for user {user_id}, category {category_name} updated to {new_amount}")

    def delete_budget(self, user_id, category_name):
        self._execute_delete_budget(user_id, category_name)
        logging.info(f"Budget for user {user_id} and category {category_name} deleted")

    # Helper methods
    def _get_existing_budget(self, user_id, category_name):
        return self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', 
            (user_id, category_name)
        ).fetchone()

    def _update_existing_budget(self, existing_budget, amount):
        budget = Budget(*existing_budget)
        logging.info(f"Updating existing budget for user {budget.user_id}, category {budget.category_name}")
        budget.amount = amount
        budget.validate()
        self.conn.execute('UPDATE budgets SET amount = ? WHERE id = ?', (budget.amount, budget.id))
        logging.info(f"Budget updated for user {budget.user_id}, category {budget.category_name}: {amount}")

    def _insert_new_budget(self, user_id, category_name, amount):
        logging.info(f"Inserting new budget for user {user_id}, category {category_name}")
        budget = Budget(None, user_id, category_name, amount, 0)
        budget.validate()
        self.conn.execute(
            'INSERT INTO budgets (user_id, category_name, amount, amount_used) VALUES (?, ?, ?, ?)', 
            (budget.user_id, budget.category_name, budget.amount, budget.amount_used)
        )
        logging.info(f"Budget set for user {user_id}, category {category_name}: {amount}")

    def _fetch_budget_row(self, user_id, category_name):
        return self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ? AND category_name = ?', 
            (user_id, category_name)
        ).fetchone()

    def _fetch_all_budget_rows(self, user_id):
        return self.conn.execute(
            'SELECT id, user_id, category_name, amount, amount_used FROM budgets WHERE user_id = ?',
            (user_id,)
        ).fetchall()

    def _execute_update_budget(self, budget):
        self.conn.execute("UPDATE budgets SET amount = ? WHERE id = ?", (budget.amount, budget.id))
        self.conn.commit()

    def _execute_delete_budget(self, user_id, category_name):
        self.conn.execute("DELETE FROM budgets WHERE user_id = ? AND category_name = ?", (user_id, category_name))
        self.conn.commit()