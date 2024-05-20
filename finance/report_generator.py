from cashflow import CashFlow


class ReportGenerator:
    @staticmethod
    def generate_balance_sheet(user):
        report = f"Balance Sheet for {user.name}\n"
        for account in user.accounts:
            report += f"Account {account.account_name}: {account.get_balance()}\n"
        return report

    @staticmethod
    def generate_income_statement(user):
        report = f"Income Statement for {user.name}\n"
        for account in user.accounts:
            for transaction in account.get_transactions():
                if transaction.amount > 0:
                    report += f"Income: {transaction}\n"
                else:
                    report += f"Expense: {transaction}\n"
        return report

    @staticmethod
    def generate_budget_report(user):
        report = f"Budget Report for {user.name}\n"
        for budget in user.budgets:
            report += f"Category {budget.category}: Spent {budget.spent}, Limit {budget.limit}\n"
        return report

    @staticmethod
    def generate_cash_flow_statement(user):
        cash_flow = CashFlow()
        for account in user.accounts:
            for transaction in account.get_transactions():
                if transaction.amount > 0:
                    cash_flow.add_inflow(transaction.amount, transaction.description)
                else:
                    cash_flow.add_outflow(transaction.amount, transaction.description)
        return cash_flow.generate_cash_flow_report()
