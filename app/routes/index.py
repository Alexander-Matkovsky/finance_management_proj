from flask import Blueprint, send_from_directory

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return send_from_directory('static', 'index.html')
