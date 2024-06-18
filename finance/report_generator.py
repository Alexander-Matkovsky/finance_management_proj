import logging
import matplotlib.pyplot as plt
import pdfkit
import tempfile
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from finance.cashflow import CashFlow
from app.models.database import UserOperations, AccountOperations, BudgetOperations, TransactionOperations

class ReportGenerator:
    def __init__(self, db):
        self.db = db
        self.accounts_db = AccountOperations(db)
        self.users_db = UserOperations(db)
        self.budgets_db = BudgetOperations(db)
        self.transaction_db = TransactionOperations(db)
        self.env = Environment(loader=FileSystemLoader('templates'))  # Adjust the path if needed

    def generate_balance_sheet(self, user):
        accounts = self.accounts_db.get_accounts(user['id'])
        total_balance = sum(account['balance'] for account in accounts)
        report_lines = [
            f"Balance Sheet for {user['name']}",
            "-" * 40
        ]
        report_lines += [f"Account {account['name']}: {account['balance']}" for account in accounts]
        report_lines.append(f"Total Balance: {total_balance}")
        return "\n".join(report_lines)

    def generate_budget_report(self, user):
        budgets = self.budgets_db.conn.execute("SELECT category_name, amount, amount_used FROM budgets WHERE user_id = ?", (user['id'],)).fetchall()
        report_lines = [
            "Budget Report",
            "-" * 40
        ]
        for budget in budgets:
            amount_used = budget["amount_used"] if budget["amount_used"] else 0
            percentage_used = (amount_used / budget["amount"]) * 100 if budget["amount"] else 0
            report_lines.append(f"Category {budget['category_name']}: amount used: {amount_used}, which is {percentage_used:.2f}% of budget, Limit {budget['amount']}")
        return "\n".join(report_lines)

    def generate_cash_flow_statement(self, user, start_date=None, end_date=None):
        cash_flow = CashFlow()
        accounts = self.accounts_db.get_accounts(user['id'])

        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        for account in accounts:
            transactions = self.transaction_db.get_transactions(account['id'])
            for transaction in transactions:
                transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                if start_date and transaction_date < start_date:
                    continue
                if end_date and transaction_date > end_date:
                    continue
                if transaction['amount'] > 0:
                    cash_flow.add_inflow(transaction['amount'], transaction['description'], transaction['date'])
                else:
                    cash_flow.add_outflow(transaction['amount'], transaction['description'], transaction['date'])
        return cash_flow.generate_cash_flow_report()

    def generate_report(self, user_id, start_date=None, end_date=None):
        user = self.users_db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."
        
        report = {
            "balance_sheet": self.generate_balance_sheet(user),
            "budget_report": self.generate_budget_report(user),
            "cash_flow_statement": self.generate_cash_flow_statement(user, start_date, end_date)
        }
        return report

    def save_report_as_pdf(self, report_html, filename):
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }
        pdfkit.from_string(report_html, filename, options=options)

    def generate_cash_flow_chart(self, user_id):
        user = self.users_db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."

        inflows, outflows = [], []
        accounts = self.accounts_db.get_accounts(user['id'])
        for account in accounts:
            transactions = self.transaction_db.get_transactions(account['id'])
            for transaction in transactions:
                if transaction['amount'] > 0:
                    inflows.append((datetime.strptime(transaction['date'], '%Y-%m-%d'), transaction['amount']))
                else:
                    outflows.append((datetime.strptime(transaction['date'], '%Y-%m-%d'), transaction['amount']))

        if inflows:
            inflow_dates, inflow_amounts = zip(*inflows)
        else:
            inflow_dates, inflow_amounts = [], []

        if outflows:
            outflow_dates, outflow_amounts = zip(*outflows)
        else:
            outflow_dates, outflow_amounts = [], []

        plt.figure(figsize=(10, 5))
        plt.plot(inflow_dates, inflow_amounts, label='Inflows', color='green')
        plt.plot(outflow_dates, outflow_amounts, label='Outflows', color='red')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.title('Cash Flows')
        plt.legend()
        plt.grid(True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name)
            plt.close()
            with open(tmpfile.name, 'rb') as f:
                chart = base64.b64encode(f.read()).decode('utf-8')
            return chart

    def generate_visual_report(self, user_id):
        user = self.users_db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."

        report = self.generate_report(user_id)
        chart = self.generate_cash_flow_chart(user_id)

        template = self.env.get_template('report.html')
        report_html = template.render(user=user, report=report, chart=chart)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
            self.save_report_as_pdf(report_html, tmpfile.name)
            pdf_path = tmpfile.name

        return pdf_path
