import os
from flask import Blueprint, request, jsonify, flash, render_template, redirect, url_for, make_response, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import get_connection, UserOperations
from app.forms import RegistrationForm, LoginForm, AdminCreationForm

bp = Blueprint('auth', __name__)

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', form=LoginForm())

    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        user = db.get_user_by_email(form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            access_token = create_access_token(identity=user.id)
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify(access_token=access_token), 200
            else:
                resp = make_response(redirect(url_for(''))) 
                set_access_cookies(resp, access_token)
                flash('Logged in successfully', 'success')
                return resp
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form), 400

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', form=RegistrationForm())

    form = RegistrationForm()
    if form.validate_on_submit():
        db = get_db()
        existing_user = db.get_user_by_email(form.email.data)
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html', form=form), 400
        
        hashed_password = generate_password_hash(form.password.data)
        new_user = db.add_user(form.name.data, form.email.data, hashed_password)
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(message='Registered successfully'), 201
        else:
            flash('Registered successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html', form=form), 400

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
    db = get_db()
    user = db.get_user(current_user_id)
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(user.__dict__), 200
    else:
        return render_template('profile.html', user=user)

@bp.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'GET':
        return render_template('create_admin.html', form=AdminCreationForm())

    form = AdminCreationForm()
    if form.validate_on_submit():
        if form.admin_secret.data != os.getenv('ADMIN_SECRET'):
            flash('Invalid admin secret', 'error')
            return render_template('create_admin.html', form=form), 400
        
        db = get_db()
        hashed_password = generate_password_hash(form.password.data)
        try:
            db.add_user(form.name.data, form.email.data, hashed_password, is_admin=True)
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify(message=f'Admin user {form.name.data} created successfully'), 201
            else:
                flash(f'Admin user {form.name.data} created successfully', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify(error=str(e)), 400
            else:
                flash(str(e), 'error')
                return render_template('create_admin.html', form=form), 400

    return render_template('create_admin.html', form=form), 400

def _get_login_params():
    return request.json.get('username'), request.json.get('password')