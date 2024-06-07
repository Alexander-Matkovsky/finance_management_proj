import logging
from flask import Blueprint, request, render_template, jsonify
from app import get_db
from finance.report_generator import ReportGenerator

bp = Blueprint('reports', __name__)

@bp.route('/generate_report', methods=['GET'])
def generate_report():
    logging.debug("Entered generate_report route")
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not user_id:
        logging.error("user_id is required")
        return jsonify({"error": "user_id is required"}), 400

    logging.debug(f"user_id: {user_id}, start_date: {start_date}, end_date: {end_date}")

    db = get_db()
    logging.debug(f"Database connection obtained: {db}")
    
    report_generator = ReportGenerator(db)
    try:
        report = report_generator.generate_report(user_id, start_date, end_date)
        logging.debug(f"Report generated successfully: {report}")
        return render_template('report.html', report=report)
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500
