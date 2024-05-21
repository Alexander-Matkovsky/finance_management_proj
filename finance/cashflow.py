class CashFlow:
    def __init__(self):
        self.inflows = []
        self.outflows = []

    def add_inflow(self, amount, description):
        self.inflows.append((amount, description))

    def add_outflow(self, amount, description):
        self.outflows.append((amount, description))  # Store outflows as positive values

    def calculate_net_cash_flow(self):
        total_inflows = sum(amount for amount, _ in self.inflows)
        total_outflows = sum(amount for amount, _ in self.outflows)
        net_cash_flow = total_inflows + total_outflows
        print(f"DEBUG: Total Inflows: {total_inflows}, Total Outflows: {total_outflows}, Net Cash Flow: {net_cash_flow}")
        return net_cash_flow

    def generate_cash_flow_report(self):
        report = "Cash Flow Report\n"
        report += "Inflows:\n"
        for amount, description in self.inflows:
            report += f"{description}: {amount}\n"
        report += "Outflows:\n"
        for amount, description in self.outflows:
            report += f"{description}: {amount}\n"  # Display outflows as positive
        net_cash_flow = self.calculate_net_cash_flow()
        report += f"Net Cash Flow: {net_cash_flow}\n"
        print(f"DEBUG: Generated Report: {report}")
        return report
