import logging
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection, UserOperations

logging.basicConfig(level=logging.DEBUG)
bp = Blueprint('dashboard', __name__, template_folder='templates')

def get_db():
    conn = get_connection()
    return UserOperations(conn)

@bp.route('/dashboard')
@jwt_required()
def dashboard():
    logging.debug("Entering dashboard route")
    try:
        current_user_id = get_jwt_identity()
        logging.debug(f"Current user ID: {current_user_id}")
        claims = get_jwt()
        logging.debug(f"JWT claims: {claims}")
        
        user_ops = get_db()
        
        user = user_ops.get_user(current_user_id)
        logging.debug(f"User retrieved: {user}")
        if not user:
            logging.warning(f"User not found for ID: {current_user_id}")
            flash("User not found", "error")
            return redirect(url_for('auth.login'))

        # Try to get total users, use a fallback if method doesn't exist
        try:
            total_users = user_ops.get_total_users()
        except AttributeError:
            logging.warning("get_total_users method not found, using fallback")
            total_users = "N/A"
        logging.debug(f"Total users: {total_users}")

        # Placeholder data
        active_projects = "N/A"
        recent_activities = ["No recent activities available"]

        logging.debug("Rendering dashboard template")
        return render_template('dashboard.html',
                               user=user,
                               total_users=total_users,
                               active_projects=active_projects,
                               recent_activities=recent_activities)
    except Exception as e:
        logging.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('auth.login'))