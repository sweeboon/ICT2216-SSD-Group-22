from flask import render_template, current_app
import logging
from itsdangerous import URLSafeTimedSerializer
from api.models import Account, OTP
from api import db
import pyotp
from datetime import datetime
from flask_mailman import EmailMessage

logger = logging.getLogger(__name__)

def send_email(subject, recipient, template, **kwargs):
    msg = EmailMessage(
        subject=subject,
        from_email=current_app.config['MAIL_DEFAULT_SENDER'],
        to=[recipient],
    )
    msg.body = render_template(f'{template}.txt', **kwargs)
    msg.html = render_template(f'{template}.html', **kwargs)
    msg.send()

def send_otp_email(recipient, otp):
    subject = "Your OTP Code"
    msg = EmailMessage(
        subject=subject,
        from_email=current_app.config['MAIL_DEFAULT_SENDER'],
        to=[recipient],
    )
    msg.body = f'Your OTP code is {otp}'
    msg.send()

def generate_and_store_otp_secret(account):
    otp_record = OTP.query.filter_by(account_id=account.account_id).first()
    otp_secret_key = pyotp.random_base32()
    if otp_record:
        otp_record.otp_secret_key = otp_secret_key
    else:
        otp_record = OTP(account_id=account.account_id, otp_secret_key=otp_secret_key)
        db.session.add(otp_record)
    db.session.commit()

def generate_otp(account):
    try:
        otp_record = OTP.query.filter_by(account_id=account.account_id).first()
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

# Used for serializing and deserializing data
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SIGNER_SECRET_KEY'])

def generate_token(data):
    serializer = get_serializer()
    salt = current_app.config['SECURITY_PASSWORD_SALT']
    logging.debug(f"Generating token with data: {data} and salt: {salt}")
    token = serializer.dumps(data, salt=salt)
    logging.debug(f"Generated token: {token}")
    return token

def verify_token(token, max_age=3600):
    serializer = get_serializer()
    salt = current_app.config['SECURITY_PASSWORD_SALT']
    logging.debug(f"Verifying token: {token} with salt: {salt}")
    try:
        data = serializer.loads(token, salt=salt, max_age=max_age)
        logging.debug(f"Token is valid, data: {data}")
        return data
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        return False
