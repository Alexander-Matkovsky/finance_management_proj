from flask import Blueprint, request, jsonify
from app.models.database import get_connection, TransactionOperations

bp = Blueprint('transactions', __name__)

def get_db():
    conn = get_connection()
    return TransactionOperations(conn)

@bp.route('/add_transaction', methods=['POST'])
def add_transaction():
    params = _get_transaction_params()
    if not all(params.values()):
        return jsonify({"error": "account_id, amount, description, category_name, date, and type are required"}), 400

    if params['type'] not in ["Income", "Expense"]:
        return jsonify({"error": "type must be either 'Income' or 'Expense'"}), 400

    try:
        params['account_id'] = int(params['account_id'])
        params['amount'] = float(params['amount'])
    except ValueError:
        return jsonify({"error": "account_id must be an integer and amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.add_transaction(
            params['account_id'],
            params['date'],
            params['amount'],
            params['type'],
            params['description'],
            params['category_name']
        ),
        success_message="Transaction added successfully!",
        status_code=201
    )

@bp.route('/delete_transaction', methods=['DELETE'])
def delete_transaction():
    transaction_id = _get_and_validate_id('transaction_id')
    if isinstance(transaction_id, tuple):
        return transaction_id

    return _execute_db_operation(
        lambda db: db.delete_transaction(transaction_id),
        success_message=f"Transaction {transaction_id} deleted successfully!"
    )

@bp.route('/get_transaction', methods=['GET'])
def get_transaction():
    transaction_id = _get_and_validate_id('transaction_id')
    if isinstance(transaction_id, tuple):
        return transaction_id

    return _execute_db_operation(
        lambda db: db.get_transaction(transaction_id),
        success_handler=lambda transaction: jsonify(dict(transaction)) if transaction else (jsonify({"error": f"Transaction {transaction_id} not found"}), 404)
    )

@bp.route('/update_transaction', methods=['PUT'])
def update_transaction():
    params = _get_transaction_params(update=True)
    if not params['transaction_id']:
        return jsonify({"error": "transaction_id is required"}), 400

    try:
        transaction_id = int(params['transaction_id'])
        amount = float(params['amount']) if params['amount'] else None
    except ValueError:
        return jsonify({"error": "transaction_id must be an integer and amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.update_transaction(
            transaction_id,
            params['date'],
            amount,
            params['type'],
            params['description'],
            params['category_name']
        ),
        success_message=f"Transaction {transaction_id} updated successfully!"
    )

@bp.route('/get_transactions', methods=['GET'])
def get_transactions():
    account_id = _get_and_validate_id('account_id')
    if isinstance(account_id, tuple):
        return account_id

    return _execute_db_operation(
        lambda db: db.get_transactions(account_id),
        success_handler=lambda transactions: jsonify(transactions)
    )

def _get_transaction_params(update=False):
    params = {
        'account_id': request.form.get('account_id'),
        'amount': request.form.get('amount'),
        'description': request.form.get('description'),
        'category_name': request.form.get('category_name'),
        'date': request.form.get('date'),
        'type': request.form.get('type')
    }
    if update:
        params['transaction_id'] = request.form.get('transaction_id')
    return params

def _get_and_validate_id(id_name):
    id_value = request.args.get(id_name)
    if not id_value:
        return jsonify({"error": f"{id_name} is required"}), 400
    try:
        return int(id_value)
    except ValueError:
        return jsonify({"error": f"{id_name} must be an integer"}), 400

def _execute_db_operation(operation, success_message=None, success_handler=None, status_code=200):
    db = get_db()
    try:
        result = operation(db)
        if success_handler:
            return success_handler(result)
        return jsonify({"message": success_message}), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500