from flask import Blueprint, send_from_directory
from flask_jwt_extended import jwt_required

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return send_from_directory('static', 'index.html')

@bp.route('/dashboard')
@jwt_required()
def dashboard():
    return send_from_directory('static', 'dashboard.html')