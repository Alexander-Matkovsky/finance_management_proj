class Account:
    def __init__(self, account_id, user_id, name, balance):
        self.account_id = account_id
        self.user_id = user_id
        self.name = name
        self.balance = balance

    def validate(self):
        if not self.name:
            raise ValueError("Account name cannot be empty")
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")

    def __str__(self):
        return f"Account(id={self.account_id}, user_id={self.user_id}, name={self.name}, balance={self.balance})"
