from flask import Blueprint, request, render_template, redirect, url_for, flash, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import BudgetOperations
from app.forms import BudgetForm, UpdateBudgetForm

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/management', methods=['GET', 'POST'])
@jwt_required()
def budget_management():
    current_user_id = get_jwt_identity()
    db = g.db
    budgets = BudgetOperations(db).get_budgets(current_user_id)
    add_form = BudgetForm()
    update_form = UpdateBudgetForm()

    if request.method == 'POST':
        if 'add_budget' in request.form:
            if add_form.validate_on_submit():
                budget_name = add_form.budget_name.data
                initial_amount = add_form.initial_amount.data
                try:
                    BudgetOperations(db).set_budget(current_user_id, budget_name, initial_amount)
                    flash(f"Budget {budget_name} added successfully!", "success")
                except Exception as e:
                    flash(str(e), "error")
            else:
                for field, errors in add_form.errors.items():
                    for error in errors:
                        flash(f"{field}: {error}", "error")
        elif 'update_budget' in request.form:
            if update_form.validate_on_submit():
                category_name = update_form.category_name.data
                new_amount = update_form.new_amount.data
                try:
                    BudgetOperations(db).update_budget(current_user_id, category_name, new_amount)
                    flash(f"Budget for category {category_name} updated successfully!", "success")
                except Exception as e:
                    flash(str(e), "error")
            else:
                for field, errors in update_form.errors.items():
                    for error in errors:
                        flash(f"{field}: {error}", "error")

    return render_template('budgets.html', budgets=budgets, add_form=add_form, update_form=update_form)

@bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_budget():
    form = BudgetForm()  # We use this just for CSRF validation
    if form.validate_on_submit():
        current_user_id = get_jwt_identity()
        category_name = request.form.get('category_name')
        if not category_name:
            flash("Category name is required", "error")
        else:
            db = g.db
            try:
                BudgetOperations(db).delete_budget(current_user_id, category_name)
                flash(f"Budget for category {category_name} deleted successfully!", "success")
            except Exception as e:
                flash(str(e), "error")
    else:
        flash("Invalid form submission", "error")
    return redirect(url_for('budgets.budget_management'))

@bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_budgets():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        flash("Admin access required", "error")
        return redirect(url_for('budgets.budget_management'))
    
    db = g.db
    try:
        budgets = BudgetOperations(db).get_all_budgets()
        return render_template('admin_budgets.html', budgets=budgets)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('budgets.budget_management'))