import unittest
from finance.budget import Budget

class TestBudget(unittest.TestCase):
    def test_add_expense(self):
        budget = Budget(1, "Groceries", 500)
        budget.add_expense(100)
        self.assertEqual(budget.spent, 100)
        self.assertEqual(budget.get_remaining_budget(), 400)

    def test_is_over_budget(self):
        budget = Budget(1, "Groceries", 500)
        budget.add_expense(600)
        self.assertTrue(budget.is_over_budget())

if __name__ == '__main__':
    unittest.main()
