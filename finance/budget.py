class Budget:
    def __init__(self, id, user_id, category_name, amount, amount_used):
        self.id = id
        self.user_id = user_id
        self.category_name = category_name
        self.amount = amount
        self.amount_used = amount_used

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_name': self.category_name,
            'amount': self.amount,
            'amount_used': self.amount_used
        }

    def validate(self):
        if not self.category_name:
            raise ValueError("Category name cannot be empty")
        if self.amount < 0:
            raise ValueError("Budget amount cannot be negative")
        if self.amount_used < 0:
            raise ValueError("Amount used cannot be negative")
        if self.amount_used > self.amount:
            raise ValueError("Amount used cannot exceed budget amount")

    def __str__(self):
        return f"Budget(id={self.id}, user_id={self.user_id}, category={self.category_name}, amount={self.amount}, used={self.amount_used})"
