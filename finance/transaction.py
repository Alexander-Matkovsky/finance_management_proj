class Transaction:
    def __init__(self, transaction_id, date, amount, category, description=""):
        self.transaction_id = transaction_id
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description

    def __str__(self):
        return f"{self.date} - {self.category}: {self.amount} ({self.description})"