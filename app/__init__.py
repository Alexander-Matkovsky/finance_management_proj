import logging
from flask import Flask, g, request, jsonify, current_app
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from app.models.database import db_connection
import os

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True  
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logging.error(f"Expired token: {jwt_payload}")
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logging.error(f"Invalid token: {error_string}")
        return jsonify({"msg": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        logging.error(f"Unauthorized: {error_string}")
        return jsonify({"msg": "Missing Authorization Header"}), 401

    # CSRF Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['WTF_CSRF_CHECK_DEFAULT'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # Set to None to prevent CSRF token expiration
    csrf = CSRFProtect(app)

    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    # Register blueprints
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
        if 'db' in g:
            g.db.close()

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token, httponly=True, samesite='Lax')
        return response

    return app

def get_db():
    if 'db' not in g:
        db_name = os.getenv('DB_NAME', 'finance.db')
        g.db = db_connection.get_connection(db_name)
    return g.db

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)