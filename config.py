import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    DB_NAME = os.getenv('DB_NAME', 'finance.db')
