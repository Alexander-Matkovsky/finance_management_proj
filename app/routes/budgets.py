from flask import Blueprint, request, jsonify
from app.models.database import get_connection, BudgetOperations

bp = Blueprint('budgets', __name__)

def get_db():
    conn = get_connection()
    return BudgetOperations(conn)

@bp.route('/add_budget', methods=['POST'])
def add_budget():
    user_id = request.form.get('user_id')
    budget_name = request.form.get('budget_name')
    initial_amount = request.form.get('initial_amount')

    if not (user_id and budget_name and initial_amount):
        return jsonify({"error": "user_id, budget_name, and initial_amount are required"}), 400

    try:
        user_id = int(user_id)
        initial_amount = float(initial_amount)
    except ValueError:
        return jsonify({"error": "user_id must be an integer and initial_amount must be a float"}), 400

    db = get_db()
    try:
        db.set_budget(user_id, budget_name, initial_amount)
        return jsonify({"message": f"Budget {budget_name} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/get_budget', methods=['GET'])
def get_budget():
    user_id = request.args.get('user_id')
    category_name = request.args.get('category_name')
    if not (user_id and category_name):
        return jsonify({"error": "user_id and category_name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        amount, amount_used = db.get_budget(user_id, category_name)
        if amount is not None:
            return jsonify({"budget": {"amount": amount, "amount_used": amount_used}}), 200
        else:
            return jsonify({"error": f"Budget for user {user_id} and category {category_name} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/get_budgets', methods=['GET'])
def get_budgets_route():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        budgets = db.get_budgets(user_id)
        if budgets:
            budgets_dict = [budget.__dict__ for budget in budgets]
            return jsonify({"budgets": budgets_dict}), 200
        else:
            return jsonify({"error": f"Budgets for user {user_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        


bp.route('/update_budget', methods=['PUT'])
def update_budget():
    user_id = request.form.get('user_id')
    category_name = request.form.get('category_name')
    new_amount = request.form.get('new_amount')

    if not (user_id and (category_name or new_amount)):
        return jsonify({"error": "user_id and at least one of category_name or new_amount are required"}), 400

    try:
        user_id = int(user_id)
        if new_amount:
            new_amount = float(new_amount)
    except ValueError:
        return jsonify({"error": "user_id must be an integer and new_amount must be a float"}), 400

    db = get_db()
    try:
        db.update_budget(user_id, category_name, new_amount)
        return jsonify({"message": f"Budget for user {user_id} and category {category_name} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_budget', methods=['DELETE'])
def delete_budget():
    user_id = request.args.get('user_id')
    category_name = request.args.get('category_name')
    if not (user_id and category_name):
        return jsonify({"error": "user_id and category_name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_budget(user_id, category_name)
        return jsonify({"message": f"Budget for user {user_id} and category {category_name} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
