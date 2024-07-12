from flask import Blueprint, request, render_template, redirect, url_for, flash, g, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import BudgetOperations
from app.forms import BudgetForm, UpdateBudgetForm
from flask_wtf.csrf import generate_csrf

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/management', methods=['GET', 'POST'])
@jwt_required()
def budget_management():
    current_user_id = get_jwt_identity()
    db = g.db
    budgets = BudgetOperations(db).get_budgets(current_user_id)
    add_form = BudgetForm()
    update_form = UpdateBudgetForm()

    # Debugging information
    print("Request method:", request.method)
    print("Form data:", request.form)
    print("CSRF token in session:", generate_csrf())
    print("CSRF token in form:", add_form.csrf_token.current_token if add_form.csrf_token else "No token")
    print("CSRF token in request:", request.headers.get('X-CSRFToken'))

    if request.method == 'POST':
        if request.is_json:
            # Handle AJAX request
            data = request.json
            if 'add_budget' in data:
                try:
                    BudgetOperations(db).set_budget(current_user_id, data['budget_name'], data['initial_amount'])
                    return jsonify({"message": f"Budget {data['budget_name']} added successfully!"}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 400
            elif 'update_budget' in data:
                try:
                    BudgetOperations(db).update_budget(current_user_id, data['category_name'], data['new_amount'])
                    return jsonify({"message": f"Budget for category {data['category_name']} updated successfully!"}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 400
        else:
            # Handle standard form submission
            if 'add_budget' in request.form and add_form.validate_on_submit():
                budget_name = add_form.budget_name.data
                initial_amount = add_form.initial_amount.data
                try:
                    BudgetOperations(db).set_budget(current_user_id, budget_name, initial_amount)
                    flash(f"Budget {budget_name} added successfully!", "success")
                except Exception as e:
                    flash(str(e), "error")
            elif 'update_budget' in request.form and update_form.validate_on_submit():
                category_name = update_form.category_name.data
                new_amount = update_form.new_amount.data
                try:
                    BudgetOperations(db).update_budget(current_user_id, category_name, new_amount)
                    flash(f"Budget for category {category_name} updated successfully!", "success")
                except Exception as e:
                    flash(str(e), "error")
            else:
                print("Form validation errors:", add_form.errors if 'add_budget' in request.form else update_form.errors)
                flash("Invalid form submission", "error")

    return render_template('budgets.html', budgets=budgets, add_form=add_form, update_form=update_form)

@bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_budget():
    current_user_id = get_jwt_identity()
    form = BudgetForm()  # We use this just for CSRF validation
    if form.validate_on_submit():
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