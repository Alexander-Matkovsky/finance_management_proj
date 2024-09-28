import os
from functools import wraps
from flask import Blueprint, request, jsonify, flash, render_template, redirect, url_for, make_response, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import get_connection, UserOperations
from app.forms.forms import RegistrationForm, LoginForm, AdminCreationForm

bp = Blueprint('auth', __name__)

def get_db():
    return UserOperations(get_connection())

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt_identity()
        if not claims.get("is_admin", False):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/check_session')
def check_session():
    user_id = get_jwt_identity()
    return jsonify({"user_id": user_id}), 200

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        user = db.get_user_by_email(form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            access_token = create_access_token(identity=user.id)
            resp = make_response(redirect(url_for('dashboard.dashboard')))
            set_access_cookies(resp, access_token)
            flash('Logged in successfully', 'success')
            return resp
        flash('Invalid email or password', 'error')
    return render_template('login.html', form=form), 200 if request.method == 'GET' else 400

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        db = get_db()
        if db.get_user_by_email(form.email.data):
            flash('Email already registered', 'error')
            return render_template('register.html', form=form), 400
        
        hashed_password = generate_password_hash(form.password.data)
        db.add_user(form.name.data, form.email.data, hashed_password)
        flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form), 200 if request.method == 'GET' else 400

@bp.route('/logout')
@jwt_required()
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(resp)
    flash('You have been logged out', 'info')
    return resp

@bp.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = get_db().get_user(current_user_id)
    return jsonify(user.__dict__) if request.is_json else render_template('profile.html', user=user)

@bp.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    form = AdminCreationForm()
    if form.validate_on_submit():
        if form.admin_secret.data != os.getenv('ADMIN_SECRET'):
            flash('Invalid admin secret', 'error')
            return render_template('create_admin.html', form=form), 400
        
        db = get_db()
        hashed_password = generate_password_hash(form.password.data)
        try:
            db.add_user(form.name.data, form.email.data, hashed_password, is_admin=True)
            flash(f'Admin user {form.name.data} created successfully', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Error creating admin user: {str(e)}")
            flash('Error creating admin user', 'error')
            return render_template('create_admin.html', form=form), 400
    return render_template('create_admin.html', form=form)