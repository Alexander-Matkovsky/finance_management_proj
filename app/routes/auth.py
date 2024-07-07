from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash
from app.models.database import user_operations
from flask_jwt_extended import get_jwt_identity

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    username, password = _get_login_params()
    if not username or password:
        return jsonify({"error": "username and password are required"}), 400
    
    user = user_operations.get_user_by_name(username)
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


def _get_login_params():
    return request.json.get('username'), request.json.get('password')