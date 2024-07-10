import logging
from flask import Flask, g
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from app.models.database import db_connection
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    jwt = JWTManager(app)

    # Configure CSRF protection
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    csrf = CSRFProtect(app)

    # Configure rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    # Secure cookie settings
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    with app.app_context():
        from .routes import users, accounts, transactions, budgets, reports, index, auth
        app.register_blueprint(users.bp)
        app.register_blueprint(accounts.bp)
        app.register_blueprint(transactions.bp)
        app.register_blueprint(budgets.bp)
        app.register_blueprint(reports.bp)
        app.register_blueprint(index.bp)
        app.register_blueprint(auth.bp)

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app

def get_db():
    if 'db' not in g:
        db_name = os.getenv('DB_NAME', 'finance.db')
        g.db = db_connection.get_connection(db_name)
    return g.db

if __name__ == "__main__":
    app = create_app()
    app.run()