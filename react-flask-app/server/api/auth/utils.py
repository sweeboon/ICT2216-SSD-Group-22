from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import pyotp
from datetime import datetime
from api.models import Account, OTP
from api.auth.email import send_otp_email
from api import db
import logging

logger = logging.getLogger(__name__)

def generate_and_store_otp_secret(account):
    otp_secret_key = pyotp.random_base32()
    new_otp = OTP(account_id=account.account_id, otp_secret_key=otp_secret_key)
    db.session.add(new_otp)
    db.session.commit()

def generate_otp(account):
    try:
        otp_record = OTP.query.filter_by(account_id=account.account_id).first()
        if not otp_record:
            generate_and_store_otp_secret(account)
            otp_record = OTP.query.filter_by(account_id=account.account_id).first()
        totp = pyotp.TOTP(otp_record.otp_secret_key, interval=300)
        otp = totp.now()
        otp_record.otp = otp
        otp_record.otp_generated_at = datetime.now()
        db.session.commit()
        return otp
    except Exception as e:
        logger.error(f'Error generating OTP: {e}')
        raise


def send_otp(account, otp):
    try:
        send_otp_email(account.email, otp)
    except Exception as e:
        logger.error(f'Error sending OTP email: {e}')
        raise

def verify_otp(account, otp):
    try:
        otp_record = OTP.query.filter_by(account_id=account.account_id).first()
        if not otp_record:
            return False

        totp = pyotp.TOTP(otp_record.otp_secret_key, interval=300)
        if not totp.verify(otp):
            return False

        otp_record.otp = None
        otp_record.otp_generated_at = None
        db.session.commit()

        return True
    except Exception as e:
        logger.error(f'Error verifying OTP: {e}')
        return False

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
