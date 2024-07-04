import logging
from flask import Flask, g
from config import Config
from app.models.database import db_connection
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
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

    return app

def get_db():
    if 'db' not in g:
        db_name = os.getenv('DB_NAME', 'finance.db')
        g.db = db_connection.get_connection(db_name)
    
    return g.db

if __name__ == "__main__":
    app = create_app()
    app.run()
