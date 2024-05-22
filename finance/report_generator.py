from finance.cashflow import CashFlow

class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def generate_balance_sheet(self, user):
        report = f"Balance Sheet for {user['name']}\n"
        accounts = self.db.conn.execute("SELECT id, name, balance FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        for account in accounts:
            report += f"Account {account['name']}: {account['balance']}\n"
        return report

    def generate_income_statement(self, user):
        report = f"Income Statement for {user['name']}\n"
        accounts = self.db.conn.execute("SELECT id, name FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        for account in accounts:
            transactions = self.db.conn.execute("SELECT amount, description FROM transactions WHERE account_id = ?", (account['id'],)).fetchall()
            for transaction in transactions:
                if transaction['amount'] > 0:
                    report += f"Income: {transaction['amount']} ({transaction['description']})\n"
                else:
                    report += f"Expense: {transaction['amount']} ({transaction['description']})\n"
        return report

    def generate_budget_report(self, user):
        report = f"Budget Report for {user['name']}\n"
        budgets = self.db.conn.execute("SELECT category_id, amount FROM budgets WHERE user_id = ?", (user['id'],)).fetchall()
        for budget in budgets:
            category = self.db.conn.execute("SELECT name FROM categories WHERE id = ?", (budget['category_id'],)).fetchone()
            spent = self.db.conn.execute("SELECT SUM(amount) FROM transactions WHERE category_id = ? AND amount < 0", (budget['category_id'],)).fetchone()[0]
            spent = spent if spent else 0
            report += f"Category {category['name']}: Spent {spent}, Limit {budget['amount']}\n"
        return report

    def generate_cash_flow_statement(self, user):
        cash_flow = CashFlow()
        accounts = self.db.conn.execute("SELECT id FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        for account in accounts:
            transactions = self.db.conn.execute("SELECT amount, description FROM transactions WHERE account_id = ?", (account['id'],)).fetchall()
            for transaction in transactions:
                if transaction['amount'] > 0:
                    cash_flow.add_inflow(transaction['amount'], transaction['description'])
                else:
                    cash_flow.add_outflow(transaction['amount'], transaction['description'])
        return cash_flow.generate_cash_flow_report()

    def generate_report(self, user_id):
        user = self.db.conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return f"User with ID {user_id} not found."

        report = ""
        report += self.generate_balance_sheet(user)
        report += "\n"
        report += self.generate_income_statement(user)
        report += "\n"
        report += self.generate_budget_report(user)
        report += "\n"
        report += self.generate_cash_flow_statement(user)
        return report
