from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, BudgetOperations

bp = Blueprint('budgets', __name__)

def get_db():
    conn = get_connection()
    return BudgetOperations(conn)

@bp.route('/add_budget', methods=['POST'])
@jwt_required()
def add_budget():
    current_user_id = get_jwt_identity()
    budget_name, initial_amount = _get_add_budget_params()
    if not all([budget_name, initial_amount]):
        return jsonify({"error": "budget_name and initial_amount are required"}), 400

    try:
        initial_amount = float(initial_amount)
    except ValueError:
        return jsonify({"error": "initial_amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.set_budget(current_user_id, budget_name, initial_amount),
        success_message=f"Budget {budget_name} added successfully!",
        status_code=201
    )

@bp.route('/get_budget', methods=['GET'])
@jwt_required()
def get_budget():
    current_user_id = get_jwt_identity()
    category_name = request.args.get('category_name')
    if not category_name:
        return jsonify({"error": "category_name is required"}), 400

    return _execute_db_operation(
        lambda db: db.get_budget(current_user_id, category_name),
        success_handler=lambda result: _handle_get_budget_result(result, current_user_id, category_name),
        not_found_message=f"Budget for category {category_name} not found"
    )

@bp.route('/get_budgets', methods=['GET'])
@jwt_required()
def get_budgets_route():
    current_user_id = get_jwt_identity()

    return _execute_db_operation(
        lambda db: db.get_budgets(current_user_id),
        success_handler=lambda budgets: jsonify({"budgets": _format_budgets(budgets)}),
        not_found_message=f"No budgets found for the user"
    )

@bp.route('/update_budget', methods=['PUT'])
@jwt_required()
def update_budget():
    current_user_id = get_jwt_identity()
    category_name, new_amount = _get_update_budget_params()
    if not (category_name and new_amount):
        return jsonify({"error": "category_name and new_amount are required"}), 400

    try:
        new_amount = float(new_amount)
    except ValueError:
        return jsonify({"error": "new_amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.update_budget(current_user_id, category_name, new_amount),
        success_message=f"Budget for category {category_name} updated successfully!"
    )

@bp.route('/delete_budget', methods=['DELETE'])
@jwt_required()
def delete_budget():
    current_user_id = get_jwt_identity()
    category_name = request.args.get('category_name')
    if not category_name:
        return jsonify({"error": "category_name is required"}), 400

    return _execute_db_operation(
        lambda db: db.delete_budget(current_user_id, category_name),
        success_message=f"Budget for category {category_name} deleted successfully!"
    )

# Admin route to view all budgets
@bp.route('/admin/all_budgets', methods=['GET'])
@jwt_required()
def get_all_budgets():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        return jsonify({"error": "Admin access required"}), 403

    return _execute_db_operation(
        lambda db: db.get_all_budgets(),
        success_handler=lambda budgets: jsonify({"budgets": _format_budgets(budgets)}),
        not_found_message="No budgets found"
    )

# Helper functions
def _get_add_budget_params():
    return (
        request.form.get('budget_name'),
        request.form.get('initial_amount')
    )

def _get_update_budget_params():
    return (
        request.form.get('category_name'),
        request.form.get('new_amount')
    )

def _format_budgets(budgets):
    budget_dicts = []
    for budget in budgets:
        if hasattr(budget, 'to_dict'):
            budget_dicts.append(budget.to_dict())
        elif isinstance(budget, dict):
            budget_dicts.append(budget)
        else:
            raise TypeError(f"Unexpected budget type: {type(budget)}")
    return budget_dicts

def _handle_get_budget_result(result, user_id, category_name):
    amount, amount_used = result
    if amount is None:
        return jsonify({"error": f"Budget for category {category_name} not found"}), 404
    return jsonify({"budget": {"amount": amount, "amount_used": amount_used}}), 200

def _execute_db_operation(operation, success_message=None, success_handler=None, not_found_message=None, status_code=200):
    db = get_db()
    try:
        result = operation(db)
        if result is None and not_found_message:
            return jsonify({"error": not_found_message}), 404
        if success_handler:
            return success_handler(result)
        return jsonify({"message": success_message}), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500