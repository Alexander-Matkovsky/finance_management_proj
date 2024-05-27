from finance.cashflow import CashFlow
import matplotlib.pyplot as plt
import pdfkit
import tempfile

class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def generate_balance_sheet(self, user):
        report = f"Balance Sheet for {user['name']}\n"
        report += "-" * 40 + "\n"
        accounts = self.db.conn.execute("SELECT id, name, balance FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        total_balance = 0
        for account in accounts:
            report += f"Account {account['name']}: {account['balance']}\n"
            total_balance += account['balance']
        report += "-" * 40 + "\n"
        report += f"Total Balance: {total_balance}\n"
        return report

    def generate_income_statement(self, user, start_date=None, end_date=None):
        report = f"Income Statement for {user['name']}\n"
        report += "-" * 40 + "\n"
        accounts = self.db.conn.execute("SELECT id, name FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        total_income = 0
        total_expenses = 0
        for account in accounts:
            transactions_query = "SELECT amount, description, date FROM transactions WHERE account_id = ?"
            params = [account['id']]
            if start_date and end_date:
                transactions_query += " AND date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            transactions = self.db.conn.execute(transactions_query, params).fetchall()
            for transaction in transactions:
                if transaction['amount'] > 0:
                    report += f"Income: {transaction['amount']} ({transaction['description']}) on {transaction['date']}\n"
                    total_income += transaction['amount']
                else:
                    report += f"Expense: {transaction['amount']} ({transaction['description']}) on {transaction['date']}\n"
                    total_expenses += transaction['amount']
        report += "-" * 40 + "\n"
        report += f"Total Income: {total_income}\n"
        report += f"Total Expenses: {total_expenses}\n"
        report += f"Net Income: {total_income + total_expenses}\n"
        return report

    def generate_budget_report(self, user):
        report = f"Budget Report for {user['name']}\n"
        report += "-" * 40 + "\n"
        budgets = self.db.conn.execute("SELECT category_id, amount FROM budgets WHERE user_id = ?", (user['id'],)).fetchall()
        for budget in budgets:
            category = self.db.conn.execute("SELECT name FROM categories WHERE id = ?", (budget['category_id'],)).fetchone()
            if category:
                spent = self.db.conn.execute("SELECT SUM(amount) FROM transactions WHERE category_id = ? AND amount < 0", (budget['category_id'],)).fetchone()[0]
                spent = spent if spent else 0
                report += f"Category {category['name']}: Spent {spent}, Limit {budget['amount']}\n"
            else:
                report += f"Category ID {budget['category_id']}: Category not found. Limit {budget['amount']}\n"
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

    def generate_summary(self, user):
        balance_sheet = self.generate_balance_sheet(user)
        income_statement = self.generate_income_statement(user)
        budget_report = self.generate_budget_report(user)
        cash_flow_statement = self.generate_cash_flow_statement(user)
        summary = "Summary\n" + "-" * 40 + "\n"
        summary += balance_sheet.split("\n")[-2] + "\n"
        summary += income_statement.split("\n")[-4] + "\n"
        summary += income_statement.split("\n")[-3] + "\n"
        summary += budget_report
        summary += cash_flow_statement.split("\n")[-1] + "\n"
        return summary

    def generate_report(self, user_id, start_date=None, end_date=None):
        user = self.db.conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return f"User with ID {user_id} not found."

        report = self.generate_summary(user)
        report += "\n"
        report += self.generate_balance_sheet(user)
        report += "\n"
        report += self.generate_income_statement(user, start_date, end_date)
        report += "\n"
        report += self.generate_budget_report(user)
        report += "\n"
        report += self.generate_cash_flow_statement(user)
        return report

    def save_report_as_pdf(self, report, filename):
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }
        pdfkit.from_string(report, filename, options=options)

    def generate_visual_report(self, user_id):
        user = self.db.conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return f"User with ID {user_id} not found."

        # Generate visual elements for the report
        cash_flow = CashFlow()
        accounts = self.db.conn.execute("SELECT id FROM accounts WHERE user_id = ?", (user['id'],)).fetchall()
        inflows = []
        outflows = []
        for account in accounts:
            transactions = self.db.conn.execute("SELECT amount, description, date FROM transactions WHERE account_id = ?", (account['id'],)).fetchall()
            for transaction in transactions:
                if transaction['amount'] > 0:
                    inflows.append((transaction['date'], transaction['amount']))
                else:
                    outflows.append((transaction['date'], transaction['amount']))

        dates, inflow_amounts = zip(*inflows) if inflows else ([], [])
        _, outflow_amounts = zip(*outflows) if outflows else ([], [])

        plt.figure(figsize=(10, 5))
        plt.plot(dates, inflow_amounts, label='Inflows')
        plt.plot(dates, outflow_amounts, label='Outflows')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.title('Cash Flows')
        plt.legend()
        plt.grid(True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name)
            plt.close()
            image_path = tmpfile.name

        report = self.generate_report(user_id)
        report += f"\n![Cash Flow Chart]({image_path})\n"
        self.save_report_as_pdf(report, f"financial_report_user_{user_id}.pdf")

        return report
