from flask import Blueprint, request, jsonify
from app.models.database import get_connection, TransactionOperations

bp = Blueprint('transactions', __name__)

def get_db():
    conn = get_connection()
    return TransactionOperations(conn)

@bp.route('/add_transaction', methods=['POST'])
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

@bp.route('/delete_transaction', methods=['DELETE'])
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

@bp.route('/get_transaction', methods=['GET'])
def get_transaction():
    transaction_id = request.args.get('transaction_id')
    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return jsonify({"error": "transaction_id must be an integer"}), 400

    db = get_db()
    try:
        transaction = db.get_transaction(transaction_id)
        if transaction:
            return jsonify(dict(transaction)), 200  # Convert sqlite3.Row to dict
        else:
            return jsonify({"error": f"Transaction {transaction_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/update_transaction', methods=['PUT'])
def update_transaction():
    transaction_id = request.form.get('transaction_id')
    account_id = request.form.get('account_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    category_name = request.form.get('category_name')
    date = request.form.get('date')
    type = request.form.get('type')

    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    try:
        transaction_id = int(transaction_id)
        if amount:
            amount = float(amount)
    except ValueError:
        return jsonify({"error": "transaction_id must be an integer and amount must be a float"}), 400
    
    db = get_db()
    try:
        db.update_transaction(transaction_id, date, amount, type, description, category_name)
        return jsonify({"message": f"Transaction {transaction_id} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/get_transactions', methods=['GET'])
def get_transactions():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "account_id must be an integer"}), 400

    db = get_db()
    try:
        transactions = db.get_transactions(account_id)
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

