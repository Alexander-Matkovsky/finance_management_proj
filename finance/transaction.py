class Transaction:
    def __init__(self, account_id, date, amount, type, description, category_name):
        self.account_id = account_id
        self.date = date
        self.amount = amount
        self.type = type
        self.description = description
        self.category_name = category_name
        self.validate()

    def validate(self):
        if not self.description:
            raise ValueError("Description cannot be empty")
        if self.type not in ["Income", "Expense"]:
            raise ValueError("Transaction type must be either 'Income' or 'Expense'")

