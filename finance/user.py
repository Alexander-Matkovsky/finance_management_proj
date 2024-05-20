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