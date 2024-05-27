class Budget:
    def __init__(self, budget_id, category_name, limit):
        self.budget_id = budget_id
        self.category_name = category_name
        self.limit = limit
        self.spent = 0

    def add_expense(self, amount):
        self.spent += amount

    def get_remaining_budget(self):
        return self.limit - self.spent

    def is_over_budget(self):
        return self.spent > self.limit
