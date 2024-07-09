from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, AccountOperations

bp = Blueprint('accounts', __name__)

def get_db():
    conn = get_connection()
    return AccountOperations(conn)

@bp.route('/add_account', methods=['POST'])
@jwt_required()
def add_account():
    current_user_id = get_jwt_identity()
    account_name, initial_balance = _get_add_account_params()
    
    if not all([account_name, initial_balance]):
        return jsonify({"error": "account_name and initial_balance are required"}), 400
    
    try:
        initial_balance = float(initial_balance)
    except ValueError:
        return jsonify({"error": "initial_balance must be a float"}), 400
    
    return _execute_db_operation(
        lambda db: db.add_account(current_user_id, account_name, initial_balance),
        success_message=f"Account {account_name} added successfully!",
        status_code=201
    )

@bp.route('/get_account', methods=['GET'])
@jwt_required()
def get_account():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "id is required"}), 400
    
    try:
        id = int(id)
    except ValueError:
        return jsonify({"error": "id must be an integer"}), 400
    
    return _execute_db_operation(
        lambda db: db.get_account(id),
        success_handler=lambda account: _check_account_access(account, current_user_id, is_admin),
        not_found_message=f"Account {id} not found"
    )

@bp.route('/update_account', methods=['PUT'])
@jwt_required()
def update_account():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    id, account_name, new_balance = _get_update_account_params()
    if not (id and (account_name or new_balance)):
        return jsonify({"error": "id and at least one of account_name or new_balance are required"}), 400
    
    try:
        id = int(id)
        new_balance = float(new_balance) if new_balance else None
    except ValueError:
        return jsonify({"error": "id must be an integer and new_balance must be a float"}), 400
    
    return _execute_db_operation(
        lambda db: _check_account_ownership(db, id, current_user_id, is_admin, 
                                            lambda: db.update_account(id, account_name, new_balance)),
        success_message=f"Account {id} updated successfully!"
    )

@bp.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "id is required"}), 400
    
    try:
        id = int(id)
    except ValueError:
        return jsonify({"error": "id must be an integer"}), 400
    
    return _execute_db_operation(
        lambda db: _check_account_ownership(db, id, current_user_id, is_admin, 
                                            lambda: db.delete_account(id)),
        success_message=f"Account {id} deleted successfully!"
    )

# Helper functions
def _get_add_account_params():
    return (
        request.form.get('account_name'),
        request.form.get('initial_balance')
    )

def _get_update_account_params():
    return (
        request.form.get('id'),
        request.form.get('account_name'),
        request.form.get('new_balance')
    )

def _account_to_dict(account):
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "balance": account.balance
    }

def _check_account_access(account, current_user_id, is_admin):
    if account.user_id == current_user_id or is_admin:
        return jsonify({"account": _account_to_dict(account)})
    else:
        return jsonify({"error": "Unauthorized access"}), 403

def _check_account_ownership(db, account_id, current_user_id, is_admin, operation):
    account = db.get_account(account_id)
    if account is None:
        return None
    if account.user_id == current_user_id or is_admin:
        return operation()
    else:
        raise PermissionError("Unauthorized access")

def _execute_db_operation(operation, success_message=None, success_handler=None, not_found_message=None, status_code=200):
    db = get_db()
    try:
        result = operation(db)
        if result is None and not_found_message:
            return jsonify({"error": not_found_message}), 404
        if success_handler:
            return success_handler(result), status_code
        return jsonify({"message": success_message}), status_code
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500