import logging
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, UserOperations
from werkzeug.security import generate_password_hash
from app.forms.forms import UpdateUserForm

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('users', __name__, template_folder='templates')

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/update_user/<int:id>', methods=['GET', 'POST'])
@jwt_required()
def update_user(id):
    logging.debug(f"Entering update_user route for user {id}")
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin and current_user_id != id:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.profile'))

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

        hashed_password = generate_password_hash(password) if password else None

        try:
            db.update_user(id, name, email, hashed_password)
            flash(f"User {id} updated successfully!", "success")
            return redirect(url_for('users.get_all_users') if is_admin else url_for('auth.profile'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")

    return render_template('update_user.html', form=form, user=user)

@bp.route('/delete_user/<int:id>', methods=['POST'])
@jwt_required()
def delete_user(id):
    logging.debug(f"Entering delete_user route for user {id}")
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.profile'))

    db = get_db()
    try:
        db.delete_user(id)
        flash(f"User {id} deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for('users.get_all_users'))

@bp.route('/admin/all_users', methods=['GET'])
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        flash("Admin access required", "error")
        return redirect(url_for('auth.profile'))

    db = get_db()
    try:
        users = db.get_all_users()
        return render_template('all_users.html', users=users)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('auth.profile'))