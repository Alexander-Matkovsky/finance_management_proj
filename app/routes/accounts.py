from flask import Blueprint, request, jsonify
from app.models.database import get_connection, AccountOperations

bp = Blueprint('accounts', __name__)

def get_db():
    conn = get_connection()
    return AccountOperations(conn)

@bp.route('/add_account', methods=['POST'])
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

@bp.route('/get_account', methods=['GET'])
def get_account():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "account_id must be an integer"}), 400

    db = get_db()
    try:
        account = db.get_account(account_id)
        if account:
            return jsonify({"account": dict(account)}), 200
        else:
            return jsonify({"error": f"Account {account_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/update_account', methods=['PUT'])
def update_account():
    account_id = request.form.get('account_id')
    account_name = request.form.get('account_name')
    new_balance = request.form.get('new_balance')

    if not (account_id and (account_name or new_balance)):
        return jsonify({"error": "account_id and at least one of account_name or new_balance are required"}), 400

    try:
        account_id = int(account_id)
        if new_balance:
            new_balance = float(new_balance)
    except ValueError:
        return jsonify({"error": "account_id must be an integer and new_balance must be a float"}), 400

    db = get_db()
    try:
        updated = db.update_account(account_id, account_name, new_balance)
        if updated:
            return jsonify({"message": f"Account {account_id} updated successfully!"}), 200
        else:
            return jsonify({"error": f"Account {account_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_account', methods=['DELETE'])
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
