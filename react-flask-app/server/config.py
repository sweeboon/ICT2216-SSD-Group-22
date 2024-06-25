import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # General configurations
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Session configurations
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = True
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REMEMBER_COOKIE_SAMESITE = "Strict"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Mail configurations
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Security configurations
    SECURITY_CONFIRMABLE = True
    SECURITY_CONFIRM_EMAIL_WITHIN = "1 days"
    SECURITY_CONFIRM_URL = '/confirm'
    SECURITY_SEND_CONFIRMATION_TEMPLATE = 'security/email/confirmation_instructions.html'
    SECURITY_EMAIL_SUBJECT_CONFIRM = "Please confirm your email"
    SECURITY_CONFIRM_ERROR_VIEW = None
    SECURITY_POST_CONFIRM_VIEW = None
    SECURITY_AUTO_LOGIN_AFTER_CONFIRM = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    SECURITY_REQUIRES_CONFIRMATION_ERROR_VIEW = None

    # Frontend configurations
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')