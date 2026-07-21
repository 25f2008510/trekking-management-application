import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trek-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trek.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False