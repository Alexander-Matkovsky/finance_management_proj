from flask import Blueprint, request, jsonify
from app import get_db

bp = Blueprint('budgets', __name__)

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
        db.add_budget(user_id, budget_name, initial_amount)
        return jsonify({"message": f"Budget {budget_name} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/get_budget', methods=['GET'])
def get_budget():
    budget_id = request.args.get('budget_id')
    if not budget_id:
        return jsonify({"error": "budget_id is required"}), 400

    try:
        budget_id = int(budget_id)
    except ValueError:
        return jsonify({"error": "budget_id must be an integer"}), 400

    db = get_db()
    try:
        budget = db.get_budget(budget_id)
        if budget:
            return jsonify({"budget": budget}), 200
        else:
            return jsonify({"error": f"Budget {budget_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/update_budget', methods=['PUT'])
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
        updated = db.update_budget(user_id, category_name, new_amount)
        if updated:
            return jsonify({"message": f"Budget {user_id} updated successfully!"}), 200
        else:
            return jsonify({"error": f"Budget {user_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_budget', methods=['DELETE'])
def delete_budget():
    user_id = request.args.get('user_id')
    category_name = request.args.get('category_name')
    if not user_id or not category_name :
        return jsonify({"error": "user_id and category_name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_budget(user_id, category_name)
        return jsonify({"message": f"Budget {category_name} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
