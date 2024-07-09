import os
from bcrypt import gensalt, hashpw
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash
from app import get_db
from flask_jwt_extended import get_jwt_identity
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import get_connection, UserOperations

bp = Blueprint('auth', __name__)



bp = Blueprint('auth', __name__)

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db = get_db()
        user = db.get_user_by_email(email)

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            return jsonify({"error": "Name, email, and password are required"}), 400

        db = get_db()
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = generate_password_hash(password)
        new_user = db.add_user(name, email, hashed_password)

        access_token = create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token), 201
    
    return render_template('register.html')

@bp.route('/logout')
@jwt_required()
def logout():
    # JWT doesn't have a built-in logout mechanism, so we'll just redirect to login
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    db = get_db()
    user = db.get_user(current_user_id)
    return render_template('profile.html', user=user)


@bp.route('/create_admin', methods=['POST'])
def create_admin():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    admin_secret = request.json.get('admin_secret')

    if admin_secret != os.getenv('ADMIN_SECRET'):
        return jsonify({"error": "Invalid admin secret"}), 403

    if not (name and email and password):
        return jsonify({"error": "Name, email, and password are required"}), 400

    hashed_password = hashpw(password.encode(), gensalt())

    db = get_db()
    try:
        db.add_user(name, email, hashed_password, is_admin=True)
        return jsonify({"message": f"Admin user {name} created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def _get_login_params():
    return request.json.get('username'), request.json.get('password')
