import logging
from flask import Blueprint, request, jsonify, render_template
from app.models.database import get_connection
from finance.report_generator import ReportGenerator

bp = Blueprint('report', __name__)

@bp.route('/generate_report', methods=['GET'])
def generate_report():
    logging.debug("Entered generate_report route")
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not user_id:
        logging.error("user_id is required")
        return jsonify({"error": "user_id is required"}), 400

    if not start_date or not end_date:
        logging.error("start_date and end_date are required")
        return jsonify({"error": "start_date and end_date are required"}), 400

    try:
        user_id = int(user_id)
    except ValueError:
        logging.error("user_id must be an integer")
        return jsonify({"error": "user_id must be an integer"}), 400

    logging.debug(f"user_id: {user_id}, start_date: {start_date}, end_date: {end_date}")

    conn = get_connection()
    logging.debug(f"Database connection obtained: {conn}")

    report_generator = ReportGenerator(conn)
    
    try:
        report = report_generator.generate_report(user_id, start_date, end_date)
        logging.debug(f"Report generated successfully: {report}")
        user = report_generator.users_db.get_user(user_id)  # Ensure user object is passed to the template
        return render_template('report.html', user=user, report=report)
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500
