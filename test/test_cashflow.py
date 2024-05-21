import unittest
from finance.cashflow import CashFlow

class TestCashFlow(unittest.TestCase):
    def test_add_inflow(self):
        cash_flow = CashFlow()
        cash_flow.add_inflow(1000, "Salary")
        self.assertEqual(cash_flow.inflows, [(1000, "Salary")])

    def test_add_outflow(self):
        cash_flow = CashFlow()
        cash_flow.add_outflow(-500, "Rent")
        self.assertEqual(cash_flow.outflows, [(-500, "Rent")])  # Outflows stored as positive values

    def test_calculate_net_cash_flow(self):
        cash_flow = CashFlow()
        cash_flow.add_inflow(1000, "Salary")
        cash_flow.add_outflow(-500, "Rent")
        self.assertEqual(cash_flow.calculate_net_cash_flow(), 500)

if __name__ == '__main__':
    unittest.main()
