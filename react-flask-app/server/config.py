import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # General configurations
    SECRET_KEY = os.environ.get("SECRET_KEY")
    OTP_SECRET_KEY = os.environ.get("OTP_SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SIGNER_SECRET_KEY = os.environ.get("SIGNER_SECRET_KEY")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET")
    
    # Session configurations
    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Mail configurations
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # CSRF configurations
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_TIME_LIMIT = None

    # Frontend configurations
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
     # disable CSRF for testing
    WTF_CSRF_ENABLED = False 