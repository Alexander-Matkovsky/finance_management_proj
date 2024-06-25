import logging
from flask import Blueprint, request, jsonify
from app.models.database import get_connection, UserOperations

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('users', __name__)

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/add_user', methods=['POST'])
def add_user():
    logging.debug("Entering add_user route")
    name = request.form.get('name')
    if not name:
        logging.error("Name is required")
        return jsonify({"error": "Name is required"}), 400
    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        db.add_user(name)
        return jsonify({"message": f"User {name} added successfully!"}), 201
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    logging.debug("Entering delete_user route")
    user_id = request.args.get('user_id')
    if not user_id:
        logging.error("user_id is required")
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        logging.error("user_id must be an integer")
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        db.delete_user(user_id)
        return jsonify({"message": f"User {user_id} deleted successfully!"}), 200
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route('/get_user', methods=['GET'])
def get_user():
    logging.debug("Entering get_user route")
    user_id = request.args.get('user_id')
    if not user_id:
        logging.error("user_id is required")
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        logging.error("user_id must be an integer")
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        user = db.get_user(user_id)
        if user:
            user_dict = {"user_id": user.user_id, "name": user.name}
            return jsonify(user_dict), 200
        else:
            return jsonify({"error": f"User {user_id} not found"}), 404
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/update_user', methods=['PUT'])
def update_user():
    logging.debug("Entering update_user route")
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    if not (user_id and name):
        logging.error("user_id and name are required")
        return jsonify({"error": "user_id and name are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        logging.error("user_id must be an integer")
        return jsonify({"error": "user_id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        db.update_user(user_id, name)
        return jsonify({"message": f"User {user_id} updated successfully!"}), 200
    except Exception as e:
        logging.error(f"Error updating user: {e}")
        return jsonify({"error": str(e)}), 500
