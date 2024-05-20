class Account:
    def __init__(self, account_id, account_name, balance=0):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.balance += transaction.amount

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions

class Transaction:
    def __init__(self, transaction_id, date, amount, category, description=""):
        self.transaction_id = transaction_id
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description

    def __str__(self):
        return f"{self.date} - {self.category}: {self.amount} ({self.description})"

class Budget:
    def __init__(self, budget_id, category, limit):
        self.budget_id = budget_id
        self.category = category
        self.limit = limit
        self.spent = 0

    def add_expense(self, amount):
        self.spent += amount

    def get_remaining_budget(self):
        return self.limit - self.spent

    def is_over_budget(self):
        return self.spent > self.limit

class CashFlow:
    def __init__(self):
        self.inflows = []
        self.outflows = []

    def add_inflow(self, amount, description):
        self.inflows.append((amount, description))

    def add_outflow(self, amount, description):
        self.outflows.append((amount, description))

    def calculate_net_cash_flow(self):
        total_inflows = sum(amount for amount, _ in self.inflows)
        total_outflows = sum(amount for amount, _ in self.outflows)
        return total_inflows - total_outflows

    def generate_cash_flow_report(self):
        report = "Cash Flow Report\n"
        report += "Inflows:\n"
        for amount, description in self.inflows:
            report += f"{description}: {amount}\n"
        report += "Outflows:\n"
        for amount, description in self.outflows:
            report += f"{description}: {amount}\n"
        report += f"Net Cash Flow: {self.calculate_net_cash_flow()}\n"
        return report

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.accounts = []
        self.budgets = []

    def add_account(self, account):
        self.accounts.append(account)

    def add_budget(self, budget):
        self.budgets.append(budget)

    def get_total_balance(self):
        return sum(account.get_balance() for account in self.accounts)

    def generate_financial_report(self):
        report = f"Financial Report for {self.name}\n"
        report += f"Total Balance: {self.get_total_balance()}\n"
        for account in self.accounts:
            report += f"Account {account.account_name}: {account.get_balance()}\n"
        return report

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
