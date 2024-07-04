from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app.models.database import user_operations

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    username, password = _get_login_params()
    if not username or password:
        return jsonify({"error": "username and password are required"}), 400
    
    user = user_operations.get_user_by_username(username)
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


def _get_login_params():
    return request.json.get('username'), request.json.get('password')