import argparse
from finance.user import User
from finance.account import Account
from finance.transaction import Transaction
from finance.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Finance Management CLI")
    
    parser.add_argument("action", choices=["add_inflow", "add_outflow", "generate_report"], help="Action to perform")
    parser.add_argument("--amount", type=float, help="Amount for the transaction")
    parser.add_argument("--description", type=str, help="Description for the transaction")
    parser.add_argument("--user_id", type=int, default=1, help="User ID")
    
    args = parser.parse_args()
    
    user = User(args.user_id, "Default User")  # Replace with actual user retrieval logic
    account = Account(1, "Checking Account", 1000)
    user.add_account(account)
    
    if args.action == "add_inflow":
        if args.amount and args.description:
            account.add_transaction(Transaction(1, "2023-05-20", args.amount, "Income", args.description))
            print(f"Added inflow: {args.amount} - {args.description}")
        else:
            print("Amount and description are required for adding inflow.")
    
    elif args.action == "add_outflow":
        if args.amount and args.description:
            account.add_transaction(Transaction(2, "2023-05-21", -args.amount, "Expense", args.description))
            print(f"Added outflow: {args.amount} - {args.description}")
        else:
            print("Amount and description are required for adding outflow.")
    
    elif args.action == "generate_report":
        report = ReportGenerator.generate_cash_flow_statement(user)
        print(report)

if __name__ == "__main__":
    main()
