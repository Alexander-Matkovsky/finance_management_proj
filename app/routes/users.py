import logging
from flask import Blueprint, request, jsonify
from app.models.database import get_connection, UserOperations
from bcrypt import hashpw, gensalt, checkpw

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('users', __name__)

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/add_user', methods=['POST'])
def add_user():
    logging.debug("Entering add_user route")
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not (name and email and password):
        return _log_and_return_error("Name, email, and password are required", 400)
    
    hashed_password = hashpw(password.encode(), gensalt())
    
    return _execute_db_operation(
        lambda db: db.add_user(name, email, hashed_password),
        success_message=f"User {name} added successfully!",
        status_code=201
    )

@bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    logging.debug("Entering delete_user route")
    id = _get_and_validate_id()
    if isinstance(id, tuple):  # Error response
        return id
    
    return _execute_db_operation(
        lambda db: db.delete_user(id),
        success_message=f"User {id} deleted successfully!"
    )

@bp.route('/get_user', methods=['GET'])
def get_user():
    logging.debug("Entering get_user route")
    id = _get_and_validate_id()
    if isinstance(id, tuple):  # Error response
        return id
    
    return _execute_db_operation(
        lambda db: db.get_user(id),
        success_handler=lambda user: jsonify({"id": user.id, "name": user.name, "email": user.email}) if user else (jsonify({"error": f"User {id} not found"}), 404)
    )

@bp.route('/update_user', methods=['PUT'])
def update_user():
    logging.debug("Entering update_user route")
    id = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not id:
        return _log_and_return_error("id is required", 400)
    
    try:
        id = int(id)
    except ValueError:
        return _log_and_return_error("id must be an integer", 400)
    
    if not (name or email or password):
        return _log_and_return_error("At least one of name, email, or password must be provided for update", 400)
    
    hashed_password = hashpw(password.encode(), gensalt()) if password else None
    
    return _execute_db_operation(
        lambda db: db.update_user(id, name, email, hashed_password),
        success_message=f"User {id} updated successfully!"
    )

def _get_and_validate_id():
    id = request.args.get('id')
    if not id:
        return _log_and_return_error("id is required", 400)
    try:
        return int(id)
    except ValueError:
        return _log_and_return_error("id must be an integer", 400)

def _log_and_return_error(message, status_code):
    logging.error(message)
    return jsonify({"error": message}), status_code

def _execute_db_operation(operation, success_message=None, success_handler=None, status_code=200):
    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    try:
        result = operation(db)
        if success_handler:
            return success_handler(result)
        return jsonify({"message": success_message}), status_code
    except Exception as e:
        return _log_and_return_error(f"Error: {str(e)}", 500)
