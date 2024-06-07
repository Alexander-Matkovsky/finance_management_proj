import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from app.models.database import db_connection

def visualize_cash_flows(account_id):
    db = db_connection.get_db()
    transactions = db.conn.execute("SELECT date, amount, type FROM transactions WHERE account_id = ?", (account_id,)).fetchall()
    
    if not transactions:
        print("No transactions found.")
        return
    
    # Creating a DataFrame for easier manipulation
    df = pd.DataFrame(transactions, columns=['date', 'amount', 'type'])

    # Splitting the transactions into inflows and outflows
    df['inflow'] = df.apply(lambda row: row['amount'] if row['type'] == 'Income' else 0, axis=1)
    df['outflow'] = df.apply(lambda row: -row['amount'] if row['type'] == 'Expense' else 0, axis=1)

    # Create a bar chart using plotly express
    fig = px.bar(df, x='date', y=['inflow', 'outflow'], title='Cash Flows', labels={'value':'Amount', 'date':'Date'}, barmode='group')

    fig.show()

def generate_report_with_plots(user_id):
    db = db_connection.get_db()
    user = db.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        print(f"No user found with ID {user_id}")
        return

    accounts = db.conn.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,)).fetchall()
    
    for account in accounts:
        account_id = account[0]
        print(f"Generating report for account: {account[2]}")

        transactions = db.conn.execute("SELECT date, amount, type, description, category_id FROM transactions WHERE account_id = ?", (account_id,)).fetchall()
        
        if transactions:
            visualize_cash_flows(account_id)
        else:
            print(f"No transactions found for account {account[2]}")
