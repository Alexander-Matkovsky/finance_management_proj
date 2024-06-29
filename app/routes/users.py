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
    id = request.args.get('id')
    if not id:
        logging.error("id is required")
        return jsonify({"error": "id is required"}), 400

    try:
        id = int(id)
    except ValueError:
        logging.error("id must be an integer")
        return jsonify({"error": "id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        db.delete_user(id)
        return jsonify({"message": f"User {id} deleted successfully!"}), 200
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route('/get_user', methods=['GET'])
def get_user():
    logging.debug("Entering get_user route")
    id = request.args.get('id')
    if not id:
        logging.error("id is required")
        return jsonify({"error": "id is required"}), 400

    try:
        id = int(id)
    except ValueError:
        logging.error("id must be an integer")
        return jsonify({"error": "id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        user = db.get_user(id)
        if user:
            user_dict = {"id": user.id, "name": user.name}
            return jsonify(user_dict), 200
        else:
            return jsonify({"error": f"User {id} not found"}), 404
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/update_user', methods=['PUT'])
def update_user():
    logging.debug("Entering update_user route")
    id = request.form.get('id')
    name = request.form.get('name')
    if not (id and name):
        logging.error("id and name are required")
        return jsonify({"error": "id and name are required"}), 400

    try:
        id = int(id)
    except ValueError:
        logging.error("id must be an integer")
        return jsonify({"error": "id must be an integer"}), 400

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        db.update_user(id, name)
        return jsonify({"message": f"User {id} updated successfully!"}), 200
    except Exception as e:
        logging.error(f"Error updating user: {e}")
        return jsonify({"error": str(e)}), 500
