from flask import Blueprint, request, jsonify, flash, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.models.database import get_connection, BudgetOperations
from app.forms import BudgetForm, UpdateBudgetForm

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

def get_db():
    conn = get_connection()
    return BudgetOperations(conn)

@bp.route('/management', methods=['GET', 'POST'])
@jwt_required()
def budget_management():
    current_app.logger.info("Entered budget_management function")
    current_user_id = get_jwt_identity()
    current_app.logger.info(f"User ID from JWT: {current_user_id}")
    db = get_db()
    
    form = BudgetForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            budget_name = form.budget_name.data
            initial_amount = form.initial_amount.data
            current_app.logger.info(f"Attempting to add budget: {budget_name}, {initial_amount}")
            try:
                db.set_budget(current_user_id, budget_name, initial_amount)
                flash(f"Budget {budget_name} added successfully!", "success")
                return redirect(url_for('budgets.budget_management'))
            except Exception as e:
                current_app.logger.error(f"Error adding budget: {str(e)}")
                flash(str(e), "error")
        else:
            current_app.logger.error(f"Form validation failed. Errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "error")
    
    budgets = db.get_budgets(current_user_id)
    return render_template('budgets.html', budgets=budgets, form=form)

    
@bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_budget():
    current_user_id = get_jwt_identity()
    form = BudgetForm()  # We use this just for CSRF validation
    if form.validate_on_submit():
        category_name = request.form.get('category_name')
        if not category_name:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify(error="Category name is required"), 400
            else:
                flash("Category name is required", "error")
        else:
            db = get_db()
            try:
                db.delete_budget(current_user_id, category_name)
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify(message=f"Budget for category {category_name} deleted successfully!"), 200
                else:
                    flash(f"Budget for category {category_name} deleted successfully!", "success")
            except Exception as e:
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify(error=str(e)), 400
                else:
                    flash(str(e), "error")
    else:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(error="Invalid form submission"), 400
        else:
            flash("Invalid form submission", "error")
    
    return redirect(url_for('budgets.budget_management'))

@bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_budgets():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(error="Admin access required"), 403
        else:
            flash("Admin access required", "error")
            return redirect(url_for('budgets.budget_management'))
    
    db = get_db()
    try:
        budgets = db.get_all_budgets()
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(budgets=[budget.__dict__ for budget in budgets]), 200
        else:
            return render_template('admin_budgets.html', budgets=budgets)
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(error=str(e)), 500
        else:
            flash(str(e), "error")
            return redirect(url_for('budgets.budget_management'))