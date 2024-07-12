from flask import Blueprint, request, render_template, redirect, url_for, flash, g, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.models.database import BudgetOperations
from app.forms import BudgetForm, UpdateBudgetForm
from flask_wtf.csrf import generate_csrf
import logging

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/management', methods=['GET', 'POST'])
@jwt_required()
def budget_management():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        logging.info(f"User ID from JWT: {current_user_id}")
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"error": "Authentication failed"}), 401

    db = g.db
    budgets = BudgetOperations(db).get_budgets(current_user_id)
    add_form = BudgetForm()
    update_form = UpdateBudgetForm()

    # Debugging information
    logging.info(f"Request method: {request.method}")
    logging.info(f"Form data: {request.form}")
    logging.info(f"CSRF token in session: {generate_csrf()}")
    logging.info(f"CSRF token in form: {add_form.csrf_token.current_token if add_form.csrf_token else 'No token'}")
    logging.info(f"CSRF token in request: {request.headers.get('X-CSRFToken')}")
    logging.info(f"Authorization header: {request.headers.get('Authorization')}")

    if request.method == 'POST':
        logging.info("Processing POST request")
        if not add_form.validate_on_submit():
            logging.error(f"Form validation failed. Errors: {add_form.errors}")
            return jsonify({"error": "Form validation failed", "details": add_form.errors}), 400

        budget_name = add_form.budget_name.data
        initial_amount = add_form.initial_amount.data
        try:
            BudgetOperations(db).set_budget(current_user_id, budget_name, initial_amount)
            flash(f"Budget {budget_name} added successfully!", "success")
            logging.info(f"Budget {budget_name} added successfully for user {current_user_id}")
        except Exception as e:
            logging.error(f"Error adding budget: {str(e)}")
            flash(str(e), "error")
            return jsonify({"error": str(e)}), 500

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