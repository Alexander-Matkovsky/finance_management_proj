class CashFlow:
    def __init__(self):
        self.inflows = []
        self.outflows = []

    def add_inflow(self, amount, description, date):
        self.inflows.append((amount, description, date))

    def add_outflow(self, amount, description, date):
        self.outflows.append((amount, description, date))  # Store outflows as positive values

    def calculate_net_cash_flow(self):
        total_inflows = sum(amount for amount, _, _ in self.inflows)
        total_outflows = sum(amount for amount, _, _ in self.outflows)
        net_cash_flow = total_inflows + total_outflows
        return net_cash_flow

    def generate_cash_flow_report(self):
        report = "Cash Flow Report\n"
        report += "Inflows:\n"
        for amount, description, date in self.inflows:
            report += f"{date} - {description}: {amount}\n"
        report += "Outflows:\n"
        for amount, description, date in self.outflows:
            report += f"{date} - {description}: {amount}\n"  # Display outflows as positive
        net_cash_flow = self.calculate_net_cash_flow()
        report += f"Net Cash Flow: {net_cash_flow}\n"
        return report
