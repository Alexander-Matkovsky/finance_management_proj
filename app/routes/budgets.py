from flask import Blueprint, request, jsonify
from app.models.database import get_connection, BudgetOperations

bp = Blueprint('budgets', __name__)

def get_db():
    conn = get_connection()
    return BudgetOperations(conn)

@bp.route('/add_budget', methods=['POST'])
def add_budget():
    user_id, budget_name, initial_amount = _get_add_budget_params()
    if not all([user_id, budget_name, initial_amount]):
        return jsonify({"error": "user_id, budget_name, and initial_amount are required"}), 400

    try:
        user_id = int(user_id)
        initial_amount = float(initial_amount)
    except ValueError:
        return jsonify({"error": "user_id must be an integer and initial_amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.set_budget(user_id, budget_name, initial_amount),
        success_message=f"Budget {budget_name} added successfully!",
        status_code=201
    )

@bp.route('/get_budget', methods=['GET'])
def get_budget():
    user_id, category_name = _get_budget_params()
    if not all([user_id, category_name]):
        return jsonify({"error": "user_id and category_name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    return _execute_db_operation(
        lambda db: db.get_budget(user_id, category_name),
        success_handler=lambda result: _handle_get_budget_result(result, user_id, category_name),
        not_found_message=f"Budget for user {user_id} and category {category_name} not found"
    )

@bp.route('/get_budgets', methods=['GET'])
def get_budgets_route():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    return _execute_db_operation(
        lambda db: db.get_budgets(user_id),
        success_handler=lambda budgets: jsonify({"budgets": _format_budgets(budgets)}),
        not_found_message=f"Budgets for user {user_id} not found"
    )

@bp.route('/update_budget', methods=['PUT'])
def update_budget():
    user_id, category_name, new_amount = _get_update_budget_params()
    if not (user_id and (category_name or new_amount)):
        return jsonify({"error": "user_id and at least one of category_name or new_amount are required"}), 400

    try:
        user_id = int(user_id)
        new_amount = float(new_amount) if new_amount else None
    except ValueError:
        return jsonify({"error": "user_id must be an integer and new_amount must be a float"}), 400

    return _execute_db_operation(
        lambda db: db.update_budget(user_id, category_name, new_amount),
        success_message=f"Budget for user {user_id} and category {category_name} updated successfully!"
    )

@bp.route('/delete_budget', methods=['DELETE'])
def delete_budget():
    user_id, category_name = _get_budget_params()
    if not all([user_id, category_name]):
        return jsonify({"error": "user_id and category_name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    return _execute_db_operation(
        lambda db: db.delete_budget(user_id, category_name),
        success_message=f"Budget for user {user_id} and category {category_name} deleted successfully!"
    )

# Helper functions
def _get_add_budget_params():
    return (
        request.form.get('user_id'),
        request.form.get('budget_name'),
        request.form.get('initial_amount')
    )

def _get_budget_params():
    return (
        request.args.get('user_id'),
        request.args.get('category_name')
    )

def _get_update_budget_params():
    return (
        request.form.get('user_id'),
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
        return jsonify({"error": f"Budget for user {user_id} and category {category_name} not found"}), 404
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