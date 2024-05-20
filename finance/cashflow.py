class CashFlow:
    def __init__(self):
        self.inflows = []
        self.outflows = []

    def add_inflow(self, amount, description):
        self.inflows.append((amount, description))

    def add_outflow(self, amount, description):
        self.outflows.append((amount, description))

    def calculate_net_cash_flow(self):
        total_inflows = sum(amount for amount, _ in self.inflows)
        total_outflows = sum(amount for amount, _ in self.outflows)
        return total_inflows - total_outflows
    
    def generate_cash_flow_report(self):
        report = "Cash Flow Report\n"
        report += "Inflows:\n"
        for amount, description in self.inflows:
            report += f"{description}: {amount}\n"
        report += "Outflows:\n"
        for amount, description in self.outflows:
            report += f"{description}: {amount}\n"
        report += f"Net Cash Flow: {self.calculate_net_cash_flow()}\n"
        return report