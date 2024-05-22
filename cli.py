import argparse
from finance.database import Database

db = Database()

def main():
    parser = argparse.ArgumentParser(description="Finance Management CLI")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # Subparser for 'add_user'
    add_user_parser = subparsers.add_parser("add_user", help="Add a new user")
    add_user_parser.add_argument("--name", type=str, required=True, help="Name of the user")

    # Subparser for 'add_account'
    add_account_parser = subparsers.add_parser("add_account", help="Add a new account")
    add_account_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    add_account_parser.add_argument("--account_name", type=str, required=True, help="Name of the account")
    add_account_parser.add_argument("--initial_balance", type=float, required=True, help="Initial balance for the account")

    # Subparser for 'add_inflow'
    add_inflow_parser = subparsers.add_parser("add_inflow", help="Add a new inflow transaction")
    add_inflow_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    add_inflow_parser.add_argument("--amount", type=float, required=True, help="Amount for the transaction")
    add_inflow_parser.add_argument("--description", type=str, required=True, help="Description for the transaction")

    # Subparser for 'add_outflow'
    add_outflow_parser = subparsers.add_parser("add_outflow", help="Add a new outflow transaction")
    add_outflow_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    add_outflow_parser.add_argument("--amount", type=float, required=True, help="Amount for the transaction")
    add_outflow_parser.add_argument("--description", type=str, required=True, help="Description for the transaction")

    # Subparser for 'generate_report'
    generate_report_parser = subparsers.add_parser("generate_report", help="Generate a report")
    generate_report_parser.add_argument("--user_id", type=int, required=True, help="User ID")

    args = parser.parse_args()

    if args.action == "add_user":
        db.add_user(args.name)
        print(f"Added user: {args.name}")

    elif args.action == "add_account":
        db.add_account(args.user_id, args.account_name, args.initial_balance)
        print(f"Added account: {args.account_name} with balance {args.initial_balance} to user {args.user_id}")

    elif args.action == "add_inflow":
        db.add_transaction(args.account_id, "2024-05-21", args.amount, "Income", args.description)
        print(f"Added inflow: {args.amount} - {args.description}")

    elif args.action == "add_outflow":
        db.add_transaction(args.account_id, "2024-05-21", -args.amount, "Expense", args.description)
        print(f"Added outflow: {args.amount} - {args.description}")

    elif args.action == "generate_report":
        generate_report(args.user_id)

def generate_report(user_id):
    user_accounts = db.conn.execute("SELECT id, name, balance FROM accounts WHERE user_id = ?", (user_id,)).fetchall()
    report = f"Report for User ID {user_id}\n"
    for account in user_accounts:
        account_id, account_name, balance = account
        transactions = db.conn.execute("SELECT date, amount, type, description FROM transactions WHERE account_id = ?", (account_id,)).fetchall()
        report += f"\nAccount: {account_name} (Balance: {balance})\n"
        for transaction in transactions:
            date, amount, type, description = transaction
            report += f"{date} - {type}: {amount} ({description})\n"
    print(report)

if __name__ == "__main__":
    main()
