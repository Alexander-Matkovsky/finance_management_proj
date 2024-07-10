from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_wtf.csrf import generate_csrf
from app.models.database import get_connection, BudgetOperations
from app.forms import BudgetForm, UpdateBudgetForm
bp = Blueprint('budgets', __name__)

def get_db():
    conn = get_connection()
    return BudgetOperations(conn)


@bp.route('/budget_management', methods=['GET'])
@jwt_required()
def budget_management():
    current_user_id = get_jwt_identity()
    db = get_db()
    budgets = db.get_budgets(current_user_id)
    add_form = BudgetForm()
    update_form = UpdateBudgetForm()
    return render_template('budgets.html', budgets=budgets, add_form=add_form, update_form=update_form, csrf_token=generate_csrf())

@bp.route('/add_budget', methods=['POST'])
@jwt_required()
def add_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        current_user_id = get_jwt_identity()
        budget_name = form.budget_name.data
        initial_amount = form.initial_amount.data

        db = get_db()
        try:
            db.set_budget(current_user_id, budget_name, initial_amount)
            flash(f"Budget {budget_name} added successfully!", "success")
        except Exception as e:
            flash(str(e), "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")

    return redirect(url_for('budgets.budget_management'))

@bp.route('/update_budget', methods=['POST'])
@jwt_required()
def update_budget():
    form = UpdateBudgetForm()
    if form.validate_on_submit():
        current_user_id = get_jwt_identity()
        category_name = form.category_name.data
        new_amount = form.new_amount.data

        db = get_db()
        try:
            db.update_budget(current_user_id, category_name, new_amount)
            flash(f"Budget for category {category_name} updated successfully!", "success")
        except Exception as e:
            flash(str(e), "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")

    return redirect(url_for('budgets.budget_management'))

@bp.route('/delete_budget', methods=['POST'])
@jwt_required()
def delete_budget():
    current_user_id = get_jwt_identity()
    category_name = request.form.get('category_name')
    if not category_name:
        flash("Category name is required", "error")
        return redirect(url_for('budgets.budget_management'))

    db = get_db()
    try:
        db.delete_budget(current_user_id, category_name)
        flash(f"Budget for category {category_name} deleted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for('budgets.budget_management'))

# Admin route to view all budgets
@bp.route('/admin/all_budgets', methods=['GET'])
@jwt_required()
def get_all_budgets():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        flash("Admin access required", "error")
        return redirect(url_for('budgets.budget_management'))

    db = get_db()
    try:
        budgets = db.get_all_budgets()
        return render_template('admin_budgets.html', budgets=budgets, csrf_token=generate_csrf())
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('budgets.budget_management'))

# Helper function (unchanged)
def _format_budgets(budgets):
    budget_dicts = []
    for budget in budgets:
        if hasattr(budget, 'to_dict'):
            budget_dicts.append(budget.to_dict())
        elif isinstance(budget, dict):
            budget_dicts.append(budget)
        else:
            raise TypeError(f"Unexpected budget type: {type(budget)}")
    return budget_dicts