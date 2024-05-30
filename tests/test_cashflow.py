import unittest
from finance.cashflow import CashFlow

class TestCashFlow(unittest.TestCase):
    def test_add_inflow(self):
        cash_flow = CashFlow()
        cash_flow.add_inflow(1000, "Salary", "2024-05-27")
        self.assertEqual(cash_flow.inflows, [(1000, "Salary", "2024-05-27")])

    def test_add_outflow(self):
        cash_flow = CashFlow()
        cash_flow.add_outflow(-500, "Rent", "2024-05-27")
        self.assertEqual(cash_flow.outflows, [(-500, "Rent", "2024-05-27")])  # Outflows stored as positive values

    def test_calculate_net_cash_flow(self):
        cash_flow = CashFlow()
        cash_flow.add_inflow(1000, "Salary", "2024-05-27")
        cash_flow.add_outflow(-500, "Rent", "2024-05-27")
        self.assertEqual(cash_flow.calculate_net_cash_flow(), 500)

if __name__ == '__main__':
    unittest.main()

