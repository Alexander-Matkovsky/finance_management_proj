from flask import Flask, request, render_template, jsonify, g
from finance.database import Database
from finance.report_generator import ReportGenerator
from finance.visualizer import visualize_cash_flows

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = Database()
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
    report = report_generator.generate_report(user_id, start_date, end_date)
    return render_template('report.html', report=report)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    db.add_user(name)
    return jsonify({"message": f"User {name} added successfully!"}), 201

@app.route('/add_account', methods=['POST'])
def add_account():
    user_id = request.form.get('user_id')
    account_name = request.form.get('account_name')
    initial_balance = request.form.get('initial_balance')
    if not (user_id and account_name and initial_balance):
        return jsonify({"error": "user_id, account_name, and initial_balance are required"}), 400
    db = get_db()
    db.add_account(user_id, account_name, initial_balance)
    return jsonify({"message": f"Account {account_name} added successfully!"}), 201

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    account_id = request.form.get('account_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    category_id = request.form.get('category_id')
    date = request.form.get('date')
    if not (account_id and amount and description and category_id and date):
        return jsonify({"error": "account_id, amount, description, category_id, and date are required"}), 400
    db = get_db()
    db.add_transaction(account_id, date, amount, "Transaction", description, category_id)
    return jsonify({"message": f"Transaction added successfully!"}), 201

@app.route('/visualize_cash_flows', methods=['GET'])
def visualize_cash_flows_route():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400
    visualize_cash_flows(account_id)
    return jsonify({"message": f"Cash flow visualization generated for account {account_id}!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
