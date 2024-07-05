from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import pyotp
from datetime import datetime
from api.models import Account
from api.auth.email import send_otp_email
from api import db
import logging

logger = logging.getLogger(__name__)

def generate_and_store_otp_secret(account):
    otp_secret_key = pyotp.random_base32()
    account.otp_secret_key = otp_secret_key
    db.session.commit()

def generate_otp(account):
    try:
        if not account.otp_secret_key:
            generate_and_store_otp_secret(account)
        totp = pyotp.TOTP(account.otp_secret_key, interval=300)
        otp = totp.now()
        return otp
    except Exception as e:
        logger.error(f'Error generating OTP: {e}')
        raise

def send_otp(account, otp):
    try:
        # Send OTP email
        from api.auth.email import send_otp_email
        send_otp_email(account.email, otp)
    except Exception as e:
        logger.error(f'Error sending OTP email: {e}')
        raise

def verify_otp(account, otp):
    try:
        if account.is_anonymous:
            raise ValueError('Account not authenticated')

        if not otp:
            raise ValueError('OTP is required')

        if not account.otp_secret_key:
            raise ValueError('OTP secret key not found')

        totp = pyotp.TOTP(account.otp_secret_key, interval=300)
        if not totp.verify(otp):
            raise ValueError('Invalid or expired OTP')

        account.otp = None
        account.otp_generated_at = None
        db.session.commit()

        return {'message': 'OTP verified successfully'}
    except Exception as e:
        logger.error(f'Error verifying OTP: {e}')
        raise

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SIGNER_SECRET_KEY'])

def generate_token(data):
    serializer = get_serializer()
    return serializer.dumps(data, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_token(token, max_age=3600):
    serializer = get_serializer()
    try:
        data = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=max_age)
    except Exception as e:
        return False
    return data
