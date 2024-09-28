import datetime
from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, TransactionOperations, AccountOperations
from app.forms.forms import TransactionForm, TransactionUpdateForm, TransactionDeleteForm

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

def get_db():
    conn = get_connection()
    return TransactionOperations(conn), AccountOperations(conn)

@bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add_transaction():
    current_user_id = get_jwt_identity()
    form = TransactionForm()
    
    if form.validate_on_submit():
        return _execute_db_operation(
            lambda db, acc_db: _check_account_ownership(acc_db, int(form.account_id.data), current_user_id, 
                lambda: db.add_transaction(
                    int(form.account_id.data),
                    form.date.data,
                    form.amount.data,
                    form.type.data,
                    form.description.data,
                    form.category_name.data
                )
            ),
            success_message="Transaction added successfully!",
            status_code=201
        )
    
    return render_template('transactions.html', form=form)

@bp.route('/update/<int:transaction_id>', methods=['GET', 'POST'])
@jwt_required()
def update_transaction(transaction_id):
    current_user_id = get_jwt_identity()
    db, acc_db = get_db()
    
    transaction = db.get_transaction(transaction_id)
    if not transaction:
        return jsonify({"error": f"Transaction {transaction_id} not found"}), 404
    
    form = TransactionUpdateForm(obj=transaction)
    
    if form.validate_on_submit():
        return _execute_db_operation(
            lambda db, acc_db: _check_transaction_ownership(db, acc_db, transaction_id, current_user_id, 
                lambda: db.update_transaction(
                    transaction_id,
                    form.date.data,
                    form.amount.data,
                    form.type.data,
                    form.description.data,
                    form.category_name.data
                )
            ),
            success_message=f"Transaction {transaction_id} updated successfully!"
        )
    
    return render_template('transactions.html', form=form)

@bp.route('/delete/<int:transaction_id>', methods=['GET', 'POST'])
@jwt_required()
def delete_transaction(transaction_id):
    current_user_id = get_jwt_identity()
    form = TransactionDeleteForm()
    
    if form.validate_on_submit():
        return _execute_db_operation(
            lambda db, acc_db: _check_transaction_ownership(db, acc_db, transaction_id, current_user_id, 
                lambda: db.delete_transaction(transaction_id)
            ),
            success_message=f"Transaction {transaction_id} deleted successfully!"
        )
    
    return render_template('delete_confirmation.html', form=form, transaction_id=transaction_id)


def _execute_db_operation(operation, success_message=None, success_handler=None, status_code=200):
    db, acc_db = get_db()
    try:
        result = operation(db, acc_db)
        if success_handler:
            return success_handler(result)
        if success_message:
            flash(success_message, 'success')
        return redirect(url_for('transactions.get_transactions'))
    except PermissionError as e:
        flash(str(e), 'error')
        return redirect(url_for('transactions.get_transactions'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('transactions.get_transactions'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('transactions.get_transactions'))

@bp.route('/get/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    current_user_id = get_jwt_identity()
    
    return _execute_db_operation(
        lambda db, acc_db: _check_transaction_ownership(db, acc_db, transaction_id, current_user_id, 
            lambda: db.get_transaction(transaction_id)
        ),
        success_handler=lambda transaction: jsonify(transaction.__dict__) if transaction else (jsonify({"error": "Transaction not found"}), 404)
    )

@bp.route('/list', methods=['GET'])
@jwt_required()
def list_transactions():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    account_id = request.args.get('account_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    category = request.args.get('category')
    
    # Convert date strings to datetime objects if provided
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    
    return _execute_db_operation(
        lambda db, acc_db: _get_user_transactions(db, acc_db, current_user_id, account_id, start_date, end_date, transaction_type, category),
        success_handler=lambda transactions: jsonify([transaction.__dict__ for transaction in transactions])
    )

def _get_transaction_params(update=False):
    params = {
        'account_id': request.form.get('account_id'),
        'amount': request.form.get('amount'),
        'description': request.form.get('description'),
        'category_name': request.form.get('category_name'),
        'date': request.form.get('date'),
        'type': request.form.get('type')
    }
    if update:
        params['transaction_id'] = request.form.get('transaction_id')
    return params

def _get_user_transactions(db, acc_db, user_id, account_id=None, start_date=None, end_date=None, transaction_type=None, category=None):
    # If account_id is provided, check ownership
    if account_id:
        _check_account_ownership(acc_db, account_id, user_id, lambda: None)
    
    # Get user's accounts
    user_accounts = acc_db.get_accounts(user_id)
    user_account_ids = [account.id for account in user_accounts]
    
    # If account_id is provided and valid, use only that account
    if account_id and account_id in user_account_ids:
        account_ids = [account_id]
    else:
        account_ids = user_account_ids
    
    # Get transactions
    transactions = db.get_transactions(
        account_ids=account_ids,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category=category
    )
    
    return transactions


def _get_and_validate_id(id_name):
    id_value = request.args.get(id_name)
    if not id_value:
        return jsonify({"error": f"{id_name} is required"}), 400
    try:
        return int(id_value)
    except ValueError:
        return jsonify({"error": f"{id_name} must be an integer"}), 400

def _check_account_ownership(acc_db, account_id, user_id, operation):
    account = acc_db.get_account(account_id)
    if account is None:
        raise ValueError(f"Account {account_id} not found")
    if account.user_id != user_id and not get_jwt().get("is_admin", False):
        raise PermissionError("Unauthorized access to this account")
    return operation()

def _check_transaction_ownership(db, acc_db, transaction_id, user_id, operation):
    transaction = db.get_transaction(transaction_id)
    if transaction is None:
        raise ValueError(f"Transaction {transaction_id} not found")
    return _check_account_ownership(acc_db, transaction.account_id, user_id, operation)

def _execute_db_operation(operation, success_message=None, success_handler=None, status_code=200):
    db, acc_db = get_db()
    try:
        result = operation(db, acc_db)
        if success_handler:
            return success_handler(result)
        return jsonify({"message": success_message}), status_code
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Admin route to view all transactions
@bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_transactions():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        return jsonify({"error": "Admin access required"}), 403

    return _execute_db_operation(
        lambda db, _: db.get_all_transactions(),
        success_handler=lambda transactions: jsonify(transactions)
    )