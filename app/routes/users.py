import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from app.models.database import get_connection, UserOperations
from bcrypt import hashpw, gensalt, checkpw
from app.forms import UserForm, UpdateUserForm

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('users', __name__, template_folder='templates')

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/add_user', methods=['GET', 'POST'])
@jwt_required()
def add_user():
    logging.debug("Entering add_user route")
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        is_new_admin = form.is_admin.data
        
        if is_new_admin and not is_admin:
            flash("Only admins can create admin users", "error")
            return redirect(url_for('users.add_user'))
        
        hashed_password = hashpw(password.encode(), gensalt())
        
        db = get_db()
        try:
            db.add_user(name, email, hashed_password, is_admin=is_new_admin)
            flash(f"User {name} added successfully!", "success")
            return redirect(url_for('users.get_all_users'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template('add_user.html', form=form, is_admin=is_admin)

@bp.route('/update_user/<int:id>', methods=['GET', 'POST'])
@jwt_required()
def update_user(id):
    logging.debug(f"Entering update_user route for user {id}")
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin and current_user_id != id:
        flash("Unauthorized access", "error")
        return redirect(url_for('users.get_all_users'))

    db = get_db()
    user = db.get_user(id)
    if not user:
        flash(f"User {id} not found", "error")
        return redirect(url_for('users.get_all_users'))

    form = UpdateUserForm(obj=user)
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = hashpw(password.encode(), gensalt()) if password else None

        try:
            db.update_user(id, name, email, hashed_password)
            flash(f"User {id} updated successfully!", "success")
            return redirect(url_for('users.get_all_users'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")

    return render_template('update_user.html', form=form, user=user)

@bp.route('/delete_user/<int:id>', methods=['POST'])
@jwt_required()
def delete_user(id):
    logging.debug(f"Entering delete_user route for user {id}")
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin and current_user_id != id:
        flash("Unauthorized access", "error")
        return redirect(url_for('users.get_all_users'))

    db = get_db()
    try:
        db.delete_user(id)
        flash(f"User {id} deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for('users.get_all_users'))

@bp.route('/get_user/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    logging.debug(f"Entering get_user route for user {id}")
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin and current_user_id != id:
        flash("Unauthorized access", "error")
        return redirect(url_for('users.get_all_users'))

    db = get_db()
    user = db.get_user(id)
    if not user:
        flash(f"User {id} not found", "error")
        return redirect(url_for('users.get_all_users'))

    return render_template('user_details.html', user=user)

@bp.route('/admin/all_users', methods=['GET'])
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        flash("Admin access required", "error")
        return redirect(url_for('main.index'))

    db = get_db()
    try:
        users = db.get_all_users()
        return render_template('all_users.html', users=users)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('main.index'))