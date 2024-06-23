import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
#load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
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
    SESSION_COOKIE_SAMESITE = 'strict'  # Restrict cookies to same-site requests
    REMEMBER_COOKIE_SAMESITE = "strict"
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
}
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)