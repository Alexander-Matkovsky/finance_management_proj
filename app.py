import os
from flask import Flask, request, render_template, jsonify, g
from finance.database import Database
from finance.report_generator import ReportGenerator
from finance.visualizer import visualize_cash_flows

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        db_name = os.getenv('DB_NAME', 'finance.db')
        g.db = Database(db_name)
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.conn.close()

@app.route('/')
def index():
    return 'Welcome to the Finance Management System!'

@app.route('/generate_report', methods=['GET'])
def generate_report():
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    db = get_db()
    report_generator = ReportGenerator(db)
    try:
        report = report_generator.generate_report(user_id, start_date, end_date)
        return render_template('report.html', report=report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    try:
        db.add_user(name)
        return jsonify({"message": f"User {name} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_account', methods=['POST'])
def add_account():
    user_id = request.form.get('user_id')
    account_name = request.form.get('account_name')
    initial_balance = request.form.get('initial_balance')

    if not (user_id and account_name and initial_balance):
        return jsonify({"error": "user_id, account_name, and initial_balance are required"}), 400

    try:
        user_id = int(user_id)
        initial_balance = float(initial_balance)
    except ValueError:
        return jsonify({"error": "user_id must be an integer and initial_balance must be a float"}), 400

    db = get_db()
    try:
        db.add_account(user_id, account_name, initial_balance)
        return jsonify({"message": f"Account {account_name} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    account_id = request.form.get('account_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    category_name = request.form.get('category_name')
    date = request.form.get('date')
    type = request.form.get('type')  # Added type for transaction

    if not (account_id and amount and description and category_name and date and type):
        return jsonify({"error": "account_id, amount, description, category_name, date, and type are required"}), 400

    if type not in ["Income", "Expense"]:
        return jsonify({"error": "type must be either 'Income' or 'Expense'"}), 400

    try:
        account_id = int(account_id)
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "account_id must be an integer and amount must be a float"}), 400

    db = get_db()
    try:
        db.add_transaction(account_id, date, amount, type, description, category_name)
        return jsonify({"message": "Transaction added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/visualize_cash_flows', methods=['GET'])
def visualize_cash_flows_route():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "account_id must be an integer"}), 400

    try:
        visualize_cash_flows(account_id)
        return jsonify({"message": f"Cash flow visualization generated for account {account_id}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_user(user_id)
        return jsonify({"message": f"User {user_id} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "account_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_account(account_id)
        return jsonify({"message": f"Account {account_id} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_transaction', methods=['DELETE'])
def delete_transaction():
    transaction_id = request.args.get('transaction_id')
    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return jsonify({"error": "transaction_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_transaction(transaction_id)
        return jsonify({"message": f"Transaction {transaction_id} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
