import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
#load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'sqlalchemy'  # Use SQLAlchemy for session storage
    SESSION_PERMANENT = True
    SESSION_SQLALCHEMY = None 
    SESSION_USE_SIGNER = True  # Encrypt the session cookie
    SESSION_SQLALCHEMY_TABLE = 'sessions'  # Name of the sessions table
    SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # Restrict cookies to same-site requests
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)