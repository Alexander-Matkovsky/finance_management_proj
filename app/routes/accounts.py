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
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "id is required"}), 400
    try:
        id = int(id)
    except ValueError:
        return jsonify({"error": "id must be an integer"}), 400
    
    db = get_db()
    try:
        account = db.get_account(id)
        if account:
            # Convert Account object to dictionary
            account_dict = {
                "id": account.id,
                "user_id": account.user_id,
                "name": account.name,
                "balance": account.balance
            }
            return jsonify({"account": account_dict}), 200
        else:
            return jsonify({"error": f"Account {id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/update_account', methods=['PUT'])
def update_account():
    id = request.form.get('id')
    account_name = request.form.get('account_name')
    new_balance = request.form.get('new_balance')

    if not (id and (account_name or new_balance)):
        return jsonify({"error": "id and at least one of account_name or new_balance are required"}), 400

    try:
        id = int(id)
        if new_balance:
            new_balance = float(new_balance)
    except ValueError:
        return jsonify({"error": "id must be an integer and new_balance must be a float"}), 400

    db = get_db()
    try:
        db.update_account(id, account_name, new_balance)
        return jsonify({"message": f"Account {id} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_account', methods=['DELETE'])
def delete_account():
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "id is required"}), 400

    try:
        id = int(id)
    except ValueError:
        return jsonify({"error": "id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_account(id)
        return jsonify({"message": f"Account {id} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
