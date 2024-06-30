from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import pyotp
from datetime import datetime
from flask import current_app
from api.models import User
from api.auth.email import send_otp_email
from api import db
import logging

logger = logging.getLogger(__name__)

def generate_otp():
    try:
        # Generate OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        otp = totp.now()
        return otp
    except Exception as e:
        logger.error(f'Error generating OTP: {e}')
        raise

def send_otp(user, otp):
    try:
        # Send OTP email
        from api.auth.email import send_otp_email
        send_otp_email(user.email, otp)
    except Exception as e:
        logger.error(f'Error sending OTP email: {e}')
        raise

def verify_otp(user, otp):
    try:
        if user.is_anonymous:
            raise ValueError('User not authenticated')

        if not otp:
            raise ValueError('OTP is required')

        # Verify OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        if not totp.verify(otp):
            raise ValueError('Invalid or expired OTP')

        user.otp = None
        user.otp_generated_at = None
        from api import db
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
        return None
    return data