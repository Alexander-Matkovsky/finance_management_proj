from flask import Blueprint, request, jsonify
from app import get_db

bp = Blueprint('users', __name__)

@bp.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    try:
        db.add_user(name)
        return jsonify({"message": f"User {name} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        db.delete_user(user_id)
        return jsonify({"message": f"User {user_id} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/get_user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        user = db.get_user(user_id)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": f"User {user_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/update_user', methods=['PUT'])
def update_user():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    if not (user_id and name):
        return jsonify({"error": "user_id and name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    try:
        db.update_user(user_id, name)
        return jsonify({"message": f"User {user_id} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500