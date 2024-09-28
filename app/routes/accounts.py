from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, AccountOperations
from app.forms.AccountsForms import AccountForm, AccountUpdateForm

bp = Blueprint('accounts', __name__, template_folder='templates')

def get_db():
    conn = get_connection()
    return AccountOperations(conn)

@bp.route('/accounts', methods=['GET'])
@jwt_required()
def list_accounts():
    current_user_id = get_jwt_identity()
    db = get_db()
    accounts = db.get_user_accounts(current_user_id)
    return render_template('accounts/list.html', accounts=accounts)

@bp.route('/add_account', methods=['GET', 'POST'])
@jwt_required()
def add_account():
    form = AccountForm()
    if form.validate_on_submit():
        current_user_id = get_jwt_identity()
        db = get_db()
        try:
            db.add_account(current_user_id, form.account_name.data, form.initial_balance.data)
            flash(f"Account {form.account_name.data} added successfully!", "success")
            return redirect(url_for('accounts.list_accounts'))
        except Exception as e:
            flash(str(e), "error")
    return render_template('accounts/add.html', form=form)

@bp.route('/edit_account/<int:id>', methods=['GET', 'POST'])
@jwt_required()
def edit_account(id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    db = get_db()
    account = db.get_account(id)
    
    if account is None:
        flash(f"Account {id} not found", "error")
        return redirect(url_for('accounts.list_accounts'))
    
    if account.user_id != current_user_id and not is_admin:
        flash("Unauthorized access", "error")
        return redirect(url_for('accounts.list_accounts'))
    
    form = AccountUpdateForm(obj=account)
    if form.validate_on_submit():
        try:
            db.update_account(id, form.account_name.data, form.new_balance.data)
            flash(f"Account {id} updated successfully!", "success")
            return redirect(url_for('accounts.list_accounts'))
        except Exception as e:
            flash(str(e), "error")
    
    return render_template('accounts/edit.html', form=form, account=account)

@bp.route('/delete_account/<int:id>', methods=['POST'])
@jwt_required()
def delete_account(id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)
    
    db = get_db()
    account = db.get_account(id)
    
    if account is None:
        flash(f"Account {id} not found", "error")
        return redirect(url_for('accounts.list_accounts'))
    
    if account.user_id != current_user_id and not is_admin:
        flash("Unauthorized access", "error")
        return redirect(url_for('accounts.list_accounts'))
    
    try:
        db.delete_account(id)
        flash(f"Account {id} deleted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")
    
    return redirect(url_for('accounts.list_accounts'))