from flask import Blueprint

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return 'Welcome to the Finance Management System!'
