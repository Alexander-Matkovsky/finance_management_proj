from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from finance.cashflow import CashFlow

class ReportGenerator:
    def __init__(self, db):
        self.db = db
        self.env = Environment(loader=FileSystemLoader('templates'))  # Adjust the path if needed

    def generate_balance_sheet(self, user):
        from app.models.database import AccountOperations
        accounts_db = AccountOperations(self.db)
        
        accounts = accounts_db.get_accounts(user.user_id)
        total_balance = sum(account.balance for account in accounts)
        report_lines = [
            f"Balance Sheet for {user.name}",
            "-" * 40
        ]
        report_lines += [f"Account {account.name}: {account.balance}" for account in accounts]
        report_lines.append(f"Total Balance: {total_balance}")
        return "\n".join(report_lines)

    def generate_budget_report(self, user):
        from app.models.database import BudgetOperations
        budgets_db = BudgetOperations(self.db)

        budgets = budgets_db.conn.execute("SELECT category_name, amount, amount_used FROM budgets WHERE user_id = ?", (user.user_id,)).fetchall()
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
        from app.models.database import AccountOperations, TransactionOperations
        accounts_db = AccountOperations(self.db)
        transaction_db = TransactionOperations(self.db)
        
        cash_flow = CashFlow()
        accounts = accounts_db.get_accounts(user.user_id)

        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        for account in accounts:
            transactions = transaction_db.get_transactions(account.account_id)
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
        from app.models.database import UserOperations
        users_db = UserOperations(self.db)
        
        user = users_db.get_user(user_id)
        if not user:
            return f"User with ID {user_id} not found."
        
        report = {
            "balance_sheet": self.generate_balance_sheet(user),
            "budget_report": self.generate_budget_report(user),
            "cash_flow_statement": self.generate_cash_flow_statement(user, start_date, end_date)
        }
        return report
