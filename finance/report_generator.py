import matplotlib.pyplot as plt
import pdfkit
import tempfile
from finance.cashflow import CashFlow
from datetime import datetime

class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def generate_balance_sheet(self, user):
        accounts = self.db.get_accounts(user['id'])
        total_balance = sum(account['balance'] for account in accounts)
        report_lines = [
            f"Balance Sheet for {user['name']}",
            "-" * 40
        ]
        report_lines += [f"Account {account['name']}: {account['balance']}" for account in accounts]
        report_lines += [
            f"Total Balance: {total_balance}"
        ]
        return "\n".join(report_lines)

    def generate_budget_report(self, user):
        budgets = self.db.conn.execute("SELECT category_name, amount, amount_used FROM budgets WHERE user_id = ?", (user['id'],)).fetchall()
        report_lines = [
            "Budget Report",
            "-" * 40
        ]
        for budget in budgets:
            amount_used = budget["amount_used"]
            amount_used = amount_used if amount_used else 0
            percentage_used = (amount_used / budget["amount"]) * 100 if budget["amount"] else 0
            report_lines.append(f"Category {budget['category_name']}: amount used: {amount_used}, which is {percentage_used:.2f}% of budget, Limit {budget['amount']}")
        return "\n".join(report_lines)


    def generate_cash_flow_statement(self, user, start_date=None, end_date=None):
        cash_flow = CashFlow()
        accounts = self.db.get_accounts(user['id'])

        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        for account in accounts:
            transactions = self.db.get_transactions(account['id'])
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

    def generate_summary(self, user):
        balance_sheet = self.generate_balance_sheet(user)
        budget_report = self.generate_budget_report(user)
        cash_flow_statement = self.generate_cash_flow_statement(user)
        summary_lines = [
            "Summary",
            "-" * 40,
            balance_sheet.split("\n")[-1],  # Total Balance
            cash_flow_statement.split("\n")[-1]  # Net Cash Flow
        ]
        return "\n".join(summary_lines)

    def generate_report(self, user_id, start_date=None, end_date=None):
        user = self.db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."
        
        report_sections = [
            self.generate_balance_sheet(user),
            self.generate_budget_report(user),
            self.generate_cash_flow_statement(user, start_date, end_date)
        ]
        return "\n\n".join(report_sections)

    def save_report_as_pdf(self, report, filename):
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }
        pdfkit.from_string(report, filename, options=options)

    def generate_visual_report(self, user_id):
        user = self.db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."

        inflows, outflows = [], []
        accounts = self.db.get_accounts(user['id'])
        for account in accounts:
            transactions = self.db.get_transactions(account['id'])
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
