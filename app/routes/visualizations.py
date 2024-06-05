from flask import Blueprint, request, jsonify
from finance.visualizer import visualize_cash_flows

bp = Blueprint('visualizations', __name__)

@bp.route('/visualize_cash_flows', methods=['GET'])
def visualize_cash_flows_route():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "account_id must be an integer"}), 400

    try:
        visualize_cash_flows(account_id)
        return jsonify({"message": f"Cash flow visualization generated for account {account_id}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
