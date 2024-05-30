import argparse
import logging
import os
from finance.database import Database
from finance.report_generator import ReportGenerator
from finance.visualizer import visualize_cash_flows

logging.basicConfig(
    filename='finance_management.log',
    filemode='a',  # append to the log file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set the logging level to DEBUG
)

def get_database():
    db_name = os.getenv("DB_NAME", "finance.db")
    return Database(db_name)

def main():
    parser = argparse.ArgumentParser(description="Finance Management CLI")
    subparsers = parser.add_subparsers(dest="action")

    # Subparser for 'add_user'
    add_user_parser = subparsers.add_parser("add_user", help="Add a new user")
    add_user_parser.add_argument("--name", required=True, help="User name")

    # Subparser for 'add_account'
    add_account_parser = subparsers.add_parser("add_account", help="Add a new account")
    add_account_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    add_account_parser.add_argument("--account_name", required=True, help="Account name")
    add_account_parser.add_argument("--initial_balance", type=float, required=True, help="Initial balance")

    # Subparser for 'add_inflow'
    add_inflow_parser = subparsers.add_parser("add_inflow", help="Add an inflow transaction")
    add_inflow_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    add_inflow_parser.add_argument("--amount", type=float, required=True, help="Amount")
    add_inflow_parser.add_argument("--description", required=True, help="Description")
    add_inflow_parser.add_argument("--category_name", required=True, help="Category Name")

    # Subparser for 'add_outflow'
    add_outflow_parser = subparsers.add_parser("add_outflow", help="Add an outflow transaction")
    add_outflow_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    add_outflow_parser.add_argument("--amount", type=float, required=True, help="Amount")
    add_outflow_parser.add_argument("--description", required=True, help="Description")
    add_outflow_parser.add_argument("--category_name", required=True, help="Category Name")

    # Subparser for 'generate_report'
    generate_report_parser = subparsers.add_parser("generate_report", help="Generate a financial report")
    generate_report_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    generate_report_parser.add_argument("--start_date", type=str, required=False, help="Start date (YYYY-MM-DD)")
    generate_report_parser.add_argument("--end_date", type=str, required=False, help="End date (YYYY-MM-DD)")

    # Subparser for 'generate_pdf_report'
    generate_pdf_report_parser = subparsers.add_parser("generate_pdf_report", help="Generate a PDF financial report")
    generate_pdf_report_parser.add_argument("--user_id", type=int, required=True, help="User ID")

    # Subparser for 'view_transactions'
    view_transactions_parser = subparsers.add_parser("view_transactions", help="View all transactions for an account")
    view_transactions_parser.add_argument("--account_id", type=int, required=True, help="Account ID")

    # Subparser for 'set_budget'
    set_budget_parser = subparsers.add_parser("set_budget", help="Set a budget for a category")
    set_budget_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    set_budget_parser.add_argument("--category_name", required=True, help="Category Name")
    set_budget_parser.add_argument("--amount", type=float, required=True, help="Budget amount")

    # Subparser for 'view_budget'
    view_budget_parser = subparsers.add_parser("view_budget", help="View budget for a category")
    view_budget_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    view_budget_parser.add_argument("--category_name", required=True, help="Category Name")

    # Subparser for 'visualize_cash_flows'
    visualize_cash_flows_parser = subparsers.add_parser("visualize_cash_flows", help="Visualize cash flows for an account")
    visualize_cash_flows_parser.add_argument("--account_id", type=int, required=True, help="Account ID")

    # Update user
    update_user_parser = subparsers.add_parser("update_user", help="Update a user")
    update_user_parser.add_argument("--user_id", type=int, required=True, help="User ID")
    update_user_parser.add_argument("--name", type=str, required=True, help="New name")

    # Update account
    update_account_parser = subparsers.add_parser("update_account", help="Update an account")
    update_account_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    update_account_parser.add_argument("--account_name", type=str, required=True, help="New account name")
    update_account_parser.add_argument("--initial_balance", type=float, required=True, help="New initial balance")

    # Update transaction
    update_transaction_parser = subparsers.add_parser("update_transaction", help="Update a transaction")
    update_transaction_parser.add_argument("--transaction_id", type=int, required=True, help="Transaction ID")
    update_transaction_parser.add_argument("--amount", type=float, required=True, help="New amount")
    update_transaction_parser.add_argument("--description", type=str, required=True, help="New description")
    update_transaction_parser.add_argument("--category_name", type=str, required=True, help="New category name")

    args = parser.parse_args()
    db = get_database()
    report_generator = ReportGenerator(db)

    try:
        if args.action == "add_user":
            db.add_user(args.name)
            logging.info(f"Added user: {args.name}")
            print(f"Added user: {args.name}")

        elif args.action == "add_account":
            db.add_account(args.user_id, args.account_name, args.initial_balance)
            logging.info(f"Added account: {args.account_name} with balance {args.initial_balance} to user {args.user_id}")
            print(f"Added account: {args.account_name} with balance {args.initial_balance} to user {args.user_id}")

        elif args.action == "add_inflow":
            db.add_transaction(args.account_id, "2024-05-21", args.amount, "Income", args.description, args.category_name)
            logging.info(f"Added inflow: {args.amount} - {args.description}")
            print(f"Added inflow: {args.amount} - {args.description}")

        elif args.action == "add_outflow":
            db.add_transaction(args.account_id, "2024-05-21", -args.amount, "Expense", args.description, args.category_name)
            logging.info(f"Added outflow: {args.amount} - {args.description}")
            print(f"Added outflow: {args.amount} - {args.description}")

        elif args.action == "generate_report":
            report = report_generator.generate_report(args.user_id, args.start_date, args.end_date)
            logging.info(f"Generated report for user {args.user_id}:\n{report}")
            print(report)

        elif args.action == "generate_pdf_report":
            report = report_generator.generate_visual_report(args.user_id)
            logging.info(f"Generated PDF report for user {args.user_id}:\n{report}")
            print(report)

        elif args.action == "view_transactions":
            view_transactions(db, args.account_id)

        elif args.action == "set_budget":
            db.set_budget(args.user_id, args.category_name, args.amount)
            logging.info(f"Set budget: {args.amount} for user {args.user_id} and category {args.category_name}")
            print(f"Set budget: {args.amount} for user {args.user_id} and category {args.category_name}")

        elif args.action == "view_budget":
            budget = db.get_budget(args.user_id, args.category_name)
            if budget:
                logging.info(f"Budget for user {args.user_id} and category {args.category_name}: {budget}")
                print(f"Budget for user {args.user_id} and category {args.category_name}: {budget}")
            else:
                print("No budget found.")

        elif args.action == "visualize_cash_flows":
            visualize_cash_flows(args.account_id)
            logging.info(f"Visualized cash flows for account {args.account_id}")

        elif args.action == "update_user":
            db.update_user(args.user_id, args.name)
            logging.info(f"Updated user {args.user_id} with new name: {args.name}")
            print(f"User {args.user_id} updated with new name: {args.name}")

        elif args.action == "update_account":
            db.update_account(args.account_id, args.account_name, args.initial_balance)
            logging.info(f"Updated account {args.account_id} with new name: {args.account_name} and initial balance: {args.initial_balance}")
            print(f"Account {args.account_id} updated with new name: {args.account_name} and initial balance: {args.initial_balance}")

        elif args.action == "update_transaction":
            db.update_transaction(args.transaction_id, args.amount, args.description, args.category_name)
            logging.info(f"Updated transaction {args.transaction_id} with new amount: {args.amount}, description: {args.description}, and category name: {args.category_name}")
            print(f"Transaction {args.transaction_id} updated with new amount: {args.amount}, description: {args.description}, and category name: {args.category_name}")

    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")

def view_transactions(db, account_id):
    transactions = db.conn.execute("SELECT date, amount, type, description, category_name FROM transactions WHERE account_id = ?", (account_id,)).fetchall()
    if not transactions:
        print("No transactions found.")
        return

    report = f"Transactions for Account ID {account_id}:\n"
    for transaction in transactions:
        date, amount, type, description, category_name = transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"{date} - {type}: {amount} ({description}) [Category: {category_name}]\n"
    print(report)

if __name__ == "__main__":
    main()
