import logging
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.database import get_connection
from finance.report_generator import ReportGenerator
from datetime import datetime, timedelta

bp = Blueprint('report', __name__)

@bp.route('/generate_report', methods=['GET'])
@jwt_required()
def generate_report():
    logging.debug("Entered generate_report route")
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    user_id, start_date, end_date = _get_report_params()

    if user_id:
        try:
            user_id = int(user_id)
            if not is_admin and user_id != current_user_id:
                logging.error("Unauthorized access attempt")
                return jsonify({"error": "Unauthorized access"}), 403
        except ValueError:
            logging.error("user_id must be an integer")
            return jsonify({"error": "user_id must be an integer"}), 400
    else:
        user_id = current_user_id

    # Set default dates if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    logging.debug(f"user_id: {user_id}, start_date: {start_date}, end_date: {end_date}")
    return _execute_report_generation(user_id, start_date, end_date)

def _get_report_params():
    return (
        request.args.get('user_id'),
        request.args.get('start_date'),
        request.args.get('end_date')
    )

def _execute_report_generation(user_id, start_date, end_date):
    conn = get_connection()
    logging.debug(f"Database connection obtained: {conn}")
    report_generator = ReportGenerator(conn)
    try:
        report = report_generator.generate_report(user_id, start_date, end_date)
        logging.debug(f"Report generated successfully: {report}")
        return render_template('report.html', report=report)
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500

# Admin route to generate report for any user
@bp.route('/admin/generate_report', methods=['GET'])
@jwt_required()
def admin_generate_report():
    logging.debug("Entered admin_generate_report route")
    claims = get_jwt()
    if not claims.get("is_admin", False):
        return jsonify({"error": "Admin access required"}), 403

    user_id, start_date, end_date = _get_report_params()
    if not user_id:
        logging.error("user_id is required for admin report generation")
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        logging.error("user_id must be an integer")
        return jsonify({"error": "user_id must be an integer"}), 400

    # Set default dates if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    logging.debug(f"user_id: {user_id}, start_date: {start_date}, end_date: {end_date}")
    return _execute_report_generation(user_id, start_date, end_date)