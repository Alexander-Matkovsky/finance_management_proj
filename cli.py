import argparse
import logging
import os
from datetime import datetime
from app.models.database import db_connection
from finance.report_generator import ReportGenerator

logging.basicConfig(
    filename='finance_management.log',
    filemode='a',  # append to the log file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set the logging level to DEBUG
)

def get_database():
    db_name = os.getenv("DB_NAME", "finance.db")
    return db_connection.get_connection(db_name)

def add_user(db, args):
    db.add_user(args.name)
    logging.info(f"Added user: {args.name}")
    print(f"Added user: {args.name}")

def add_account(db, args):
    db.add_account(args.user_id, args.account_name, args.initial_balance)
    logging.info(f"Added account: {args.account_name} with balance {args.initial_balance} to user {args.user_id}")
    print(f"Added account: {args.account_name} with balance {args.initial_balance} to user {args.user_id}")

def add_transaction(db, args, transaction_type):
    date = datetime.now().strftime('%Y-%m-%d')
    amount = args.amount if transaction_type == "Income" else -args.amount
    db.add_transaction(args.account_id, date, amount, transaction_type, args.description, args.category_name)
    logging.info(f"Added {transaction_type.lower()}: {args.amount} - {args.description}")
    print(f"Added {transaction_type.lower()}: {args.amount} - {args.description}")

def transfer_between_accounts(db, args):
    date = datetime.now().strftime('%Y-%m-%d')
    db.transfer_between_accounts(args.from_account_id, args.to_account_id, date, args.amount, args.description)
    logging.info(f"Transferred {args.amount} from account {args.from_account_id} to account {args.to_account_id}: {args.description}")
    print(f"Transferred {args.amount} from account {args.from_account_id} to account {args.to_account_id}: {args.description}")

def generate_report(db, args, report_generator):
    report = report_generator.generate_report(args.user_id, args.start_date, args.end_date)
    logging.info(f"Generated report for user {args.user_id}:\n{report}")
    print(report)

def generate_pdf_report(db, args, report_generator):
    report = report_generator.generate_visual_report(args.user_id)
    logging.info(f"Generated PDF report for user {args.user_id}:\n{report}")
    print(report)

def view_transactions(db, args):
    transactions = db.conn.execute("SELECT date, amount, type, description, category_name FROM transactions WHERE account_id = ?", (args.account_id,)).fetchall()
    if not transactions:
        print("No transactions found.")
        return

    report = f"Transactions for Account ID {args.account_id}:\n"
    for transaction in transactions:
        date, amount, type, description, category_name = transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"{date} - {type}: {amount} ({description}) [Category: {category_name}]\n"
    print(report)

def set_budget(db, args):
    db.set_budget(args.user_id, args.category_name, args.amount)
    logging.info(f"Set budget: {args.amount} for user {args.user_id} and category {args.category_name}")
    print(f"Set budget: {args.amount} for user {args.user_id} and category {args.category_name}")

def view_budget(db, args):
    budget = db.get_budget(args.user_id, args.category_name)
    if budget:
        logging.info(f"Budget for user {args.user_id} and category {args.category_name}: {budget}")
        print(f"Budget for user {args.user_id} and category {args.category_name}: {budget}")
    else:
        print("No budget found.")

def update_user(db, args):
    db.update_user(args.user_id, args.name)
    logging.info(f"Updated user {args.user_id} with new name: {args.name}")
    print(f"User {args.user_id} updated with new name: {args.name}")

def update_account(db, args):
    db.update_account(args.account_id, args.account_name, args.initial_balance)
    logging.info(f"Updated account {args.account_id} with new name: {args.account_name} and initial balance: {args.initial_balance}")
    print(f"Account {args.account_id} updated with new name: {args.account_name} and initial balance: {args.initial_balance}")

def update_transaction(db, args):
    db.update_transaction(args.transaction_id, args.amount, args.description, args.category_name)
    logging.info(f"Updated transaction {args.transaction_id} with new amount: {args.amount}, description: {args.description}, and category name: {args.category_name}")
    print(f"Transaction {args.transaction_id} updated with new amount: {args.amount}, description: {args.description}, and category name: {args.category_name}")


def delete_user(db, args):
    db.delete_user(args.user_id)
    logging.info(f"Deleted user {args.user_id}")
    print(f"Deleted user {args.user_id}")

def delete_account(db, args):
    db.delete_account(args.account_id)
    logging.info(f"Deleted account {args.account_id}")
    print(f"Deleted account {args.account_id}")

def delete_transaction(db, args):
    db.delete_transaction(args.transaction_id)
    logging.info(f"Deleted transaction {args.transaction_id}")
    print(f"Deleted transaction {args.transaction_id}")

def delete_budget(db, args):
    db.delete_budget(args.user_id, args.category_name)
    logging.info(f"Deleted budget for user {args.user_id} and category {args.category_name}")
    print(f"Deleted budget for user {args.user_id} and category {args.category_name}")

def view_users(db):
    users = db.get_users()
    if not users:
        print("No users found.")
        return

    report = "Users:\n"
    for user in users:
        user_id, name = user['user_id'], user['name']
        report += f"User ID: {user_id}, Name: {name}\n"
    print(report)

def view_accounts(db):
    accounts = db.get_accounts()
    if not accounts:
        print("No accounts found.")
        return
    report = "Accounts:\n"
    for account in accounts:
        account_id, user_id, account_name, balance = account['account_id'], account['user_id'], account['account_name'], account['balance']
        report += f"Account ID: {account_id}, User ID: {user_id}, Account Name: {account_name}, Balance: {balance}\n"
    print(report)

def view_transactions_by_user(db, args):
    transactions = db.get_transactions_by_user(args.user_id)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for User ID {args.user_id}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_account(db, args):
    transactions = db.get_transactions_by_account(args.account_id)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for Account ID {args.account_id}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_category(db, args):
    transactions = db.get_transactions_by_category(args.category_name)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for Category Name {args.category_name}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_date(db, args):
    transactions = db.get_transactions_by_date(args.start_date, args.end_date)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions from {args.start_date} to {args.end_date}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_type(db, args):
    transactions = db.get_transactions_by_type(args.type)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for Type {args.type}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_description(db, args):
    transactions = db.get_transactions_by_description(args.description)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for Description {args.description}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)

def view_transactions_by_category_and_type(db, args):
    transactions = db.get_transactions_by_category_and_type(args.category_name, args.type)
    if not transactions:
        print("No transactions found.")
        return
    report = f"Transactions for Category Name {args.category_name} and Type {args.type}:\n"
    for transaction in transactions:
        transaction_id, account_id, date, amount, type, description, category_name = transaction['transaction_id'], transaction['account_id'], transaction['date'], transaction['amount'], transaction['type'], transaction['description'], transaction['category_name']
        report += f"Transaction ID: {transaction_id}, Account ID: {account_id}, Date: {date}, Amount: {amount}, Type: {type}, Description: {description}, Category Name: {category_name}\n"
    print(report)    

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

      # Subparser for 'transfer'
    transfer_parser = subparsers.add_parser("transfer", help="Transfer between accounts")
    transfer_parser.add_argument("--from_account_id", type=int, required=True, help="From Account ID")
    transfer_parser.add_argument("--to_account_id", type=int, required=True, help="To Account ID")
    transfer_parser.add_argument("--amount", type=float, required=True, help="Amount")
    transfer_parser.add_argument("--description", required=True, help="Description")

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

    # View transactions by date
    view_transactions_by_date_parser = subparsers.add_parser("view_transactions_by_date", help="View transactions by date")
    view_transactions_by_date_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    view_transactions_by_date_parser.add_argument("--start_date", type=str, required=True, help="Start date (YYYY-MM-DD)")
    view_transactions_by_date_parser.add_argument("--end_date", type=str, required=True, help="End date (YYYY-MM-DD)")

    # View transactions by type
    view_transactions_by_type_parser = subparsers.add_parser("view_transactions_by_type", help="View transactions by type")
    view_transactions_by_type_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    view_transactions_by_type_parser.add_argument("--type", type=str, required=True, help="Type (Income or Expense)")

    # View transactions by description
    view_transactions_by_description_parser = subparsers.add_parser("view_transactions_by_description", help="View transactions by description")
    view_transactions_by_description_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    view_transactions_by_description_parser.add_argument("--description", type=str, required=True, help="Description")

    # View transactions by category and type
    view_transactions_by_category_and_type_parser = subparsers.add_parser("view_transactions_by_category_and_type", help="View transactions by category and type")
    view_transactions_by_category_and_type_parser.add_argument("--account_id", type=int, required=True, help="Account ID")
    view_transactions_by_category_and_type_parser.add_argument("--category_name", type=str, required=True, help="Category Name")
    view_transactions_by_category_and_type_parser.add_argument("--type", type=str, required=True, help="Type (Income or Expense)")

    args = parser.parse_args()
    db = get_database()
    report_generator = ReportGenerator(db)

    actions = {
        "add_user": lambda: add_user(db, args),
        "add_account": lambda: add_account(db, args),
        "add_inflow": lambda: add_transaction(db, args, "Income"),
        "add_outflow": lambda: add_transaction(db, args, "Expense"),
        "transfer": lambda: transfer_between_accounts(db, args),
        "generate_report": lambda: generate_report(db, args, report_generator),
        "generate_pdf_report": lambda: generate_pdf_report(db, args, report_generator),
        "view_transactions": lambda: view_transactions(db, args),
        "set_budget": lambda: set_budget(db, args),
        "view_budget": lambda: view_budget(db, args),
        "update_user": lambda: update_user(db, args),
        "update_account": lambda: update_account(db, args),
        "update_transaction": lambda: update_transaction(db, args),
        "view_transactions_by_date": lambda: view_transactions_by_date(db, args),
        "view_transactions_by_type": lambda: view_transactions_by_type(db, args),
        "view_transactions_by_description": lambda: view_transactions_by_description(db, args),
        "view_transactions_by_category_and_type": lambda: view_transactions_by_category_and_type(db, args)
    }

    try:
        if args.action in actions:
            actions[args.action]()
        else:
            parser.print_help()
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
