from flask import Flask, g
from config import Config
from app.models.database import Database
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        from .routes import users, accounts, transactions, budgets, reports, visualizations

        app.register_blueprint(users.bp)
        app.register_blueprint(accounts.bp)
        app.register_blueprint(transactions.bp)
        app.register_blueprint(budgets.bp)
        app.register_blueprint(reports.bp)
        app.register_blueprint(visualizations.bp)

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.conn.close()
    return app

def get_db():
    if 'db' not in g:
        db_name = os.getenv('DB_NAME', 'finance.db')
        g.db = Database(db_name)
    return g.db


