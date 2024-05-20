class Account:
    def __init__(self, account_id, account_name, balance=-1):
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