from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import Account, Role, LoginAttempt
from api import db, csrf, mail, limiter
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .utils import generate_token, verify_token, generate_otp, send_otp, verify_otp, send_email
import jwt
from flask_wtf.csrf import generate_csrf
import logging
import pyotp
import secrets
import bleach, re
from flask import Flask
from api.admin.routes import log_audit_event, get_ip_address  # Import the function
from flask_limiter.errors import RateLimitExceeded


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15)

def validate_email(email):
    email_regex = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(email_regex, email)

def sanitize_input(input):
    return bleach.clean(input, strip=True)

def validate_password(password):
    if len(password) < 12:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
        return False
    if not any(char.isalpha() for char in password):  # Check for letters
        return False
    return True

# Custom error handler for rate limit exceeded
@bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded", message="You have hit the rate limit for sending too many requests. Please try again later."), 429

@bp.route('/reset_password_request', methods=['POST'])
@csrf.exempt
@limiter.limit("1 per minute") # Apply rate limiting
def reset_password_request():
    data = request.get_json()
    email = data.get('email')
    account = Account.query.filter_by(email=email).first()

    if account:
        now = datetime.now()
        if account.confirmation_email_sent_at and now < account.confirmation_email_sent_at + timedelta(minutes=1):
            return jsonify({'message': 'Password reset link already sent. Please wait a minute before requesting a new one.'}), 400

        token = generate_token(account.email)
        reset_url = f"{current_app.config['FRONTEND_BASE_URL']}/reset-password?token={token}"
        send_email('Reset Your Password', account.email, 'email/reset_password', reset_url=reset_url)
        account.confirmation_email_sent_at = now
        db.session.commit()
        log_audit_event(account.account_id, account.name, 'Reset Password Request', 'Password reset link sent', get_ip_address())
    return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200

@bp.route('/reset_password', methods=['POST'])
@csrf.exempt
@limiter.limit("1 per minute") # Apply rate limiting
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    email = verify_token(token)
    if email is False:
        return jsonify({'error': 'Invalid or expired token'}), 400

    account = Account.query.filter_by(email=email).first()
    if not account:
        return jsonify({'error': 'Invalid email address'}), 404

    if not validate_password(new_password):
        return jsonify({'error': 'Password must be at least 12 characters long, contain at least one number, and one special character'}), 400

    account.password = pbkdf2_sha256.hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password reset successful'}), 200

@bp.route('/resend_confirmation_email', methods=['POST'])
@csrf.exempt
@limiter.limit("1 per minute") # Apply rate limiting
def resend_confirmation_email():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400

    account = Account.query.filter_by(email=data['email']).first()
    if account is None:
        return jsonify({'message': 'Invalid email address'}), 401

    if account.confirmed:
        return jsonify({'message': 'Account already confirmed. Please login.'}), 200

    now = datetime.now()
    if account.confirmation_email_sent_at and now < account.confirmation_email_sent_at + timedelta(minutes=1):
        log_audit_event(account.account_id, account.name, 'Resend Confirmation Email', 'Confirmation email resent', get_ip_address())
        return jsonify({'message': 'Confirmation email already sent. Please wait a minute before requesting a new one.'}), 400

    token = generate_token(account.email)
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm?token={token}"
    send_email('Confirm Your Account', account.email, 'email/confirm', confirm_url=confirm_url)

    account.confirmation_token = token  
    account.confirmation_email_sent_at = now  
    db.session.commit()
    log_audit_event(account.account_id, account.name, 'Resend Confirmation Email', 'Confirmation email resent', get_ip_address())
    return jsonify({'message': 'Confirmation email sent. Please check your email.'}), 200

@bp.route('/initiate_login', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def initiate_login():
    data = request.get_json()
    logger.debug('Received data for initiate_login: %s', data)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logger.debug('Email or password not provided')
        return jsonify({'message': 'Email and password are required'}), 400

    if not validate_email(email):
        logger.debug('Invalid email format: %s', email)
        return jsonify({'message': 'Invalid email format'}), 400

    email = sanitize_input(email)
    password = sanitize_input(password)

    account = Account.query.filter_by(email=email).first()
    if account is None:
        logger.debug('Account not found for email: %s', email)
        return jsonify({'message': 'Invalid email or password'}), 401

    if not account.confirmed:
        logger.debug('Account not confirmed for email: %s', email)
        return jsonify({
            'message': 'Account not confirmed. Do you want to resend the confirmation email?',
            'resend_confirmation': True
        }), 403

    login_attempt = LoginAttempt.query.filter_by(account_id=account.account_id).first()
    if not login_attempt:
        logger.debug('Creating new login attempt record for account id: %s', account.account_id)
        login_attempt = LoginAttempt(account_id=account.account_id)
        db.session.add(login_attempt)
        db.session.commit()

    if login_attempt.lockout_time and datetime.now() < login_attempt.lockout_time:
        logger.debug('Account is locked for email: %s', email)
        log_audit_event(account.account_id, account.name, "Rate Limiting", "Locked User's Account", get_ip_address())
        return jsonify({'message': 'Account is locked. Please try again later.'}), 403

    if not pbkdf2_sha256.verify(password, account.password):
        logger.debug('Invalid password for email: %s', email)
        login_attempt.failed_attempts += 1
        if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
            login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
        db.session.commit()
        return jsonify({'message': 'Invalid email or password'}), 401

    login_attempt.failed_attempts = 0
    db.session.commit()

    otp = generate_otp(account)
    send_otp(account, otp)
    logger.debug('OTP sent to email: %s', email)
    return jsonify({'message': 'OTP sent to email.', 'otp_required': True}), 200

@bp.route('/verify_otp_and_login', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute", error_message="Too many requests. Please try again later.") # Apply rate limiting
def verify_otp_and_login():
    print('verify_otp_and_login route hit')
    data = request.get_json()
    logger.debug('Received data for verify_otp_and_login: %s', data)

    if 'email' not in data or 'otp' not in data:
        logger.debug('Email or OTP not in data')
        return jsonify({'message': 'Email and OTP are required'}), 400

    account = Account.query.filter_by(email=data['email']).first()
    if account is None:
        logger.debug('Account not found for email: %s', data['email'])
        return jsonify({'message': 'Invalid email address'}), 401

    login_attempt = LoginAttempt.query.filter_by(account_id=account.account_id).first()
    if login_attempt.lockout_time and datetime.now() < login_attempt.lockout_time:
        logger.debug('Account is locked for email: %s', data['email'])
        log_audit_event(account.account_id, account.name, "Rate Limiting", "Locked User;s account", get_ip_address())
        return jsonify({'message': 'Account is locked. Please try again later.'}), 403

    try:
        if verify_otp(account, data['otp']):
            logger.debug('OTP verified for email: %s', data['email'])
            login_attempt.failed_attempts = 0
            login_attempt.lockout_time = None
            login_attempt.last_login_at = datetime.now()
            login_attempt.login_count += 1
            db.session.commit()

            # Clear existing session to ensure new session starts clean
            session.clear()

            token = jwt.encode({
                'sub': account.email,
                'iat': datetime.now(),
                'exp': datetime.now() + timedelta(minutes=30)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            login_user(account, remember=True, duration=timedelta(minutes=30))
            identity_changed.send(current_app._get_current_object(), identity=Identity(account.account_id))
            roles = [role.name for role in account.roles]

            response = make_response(jsonify({'message': 'Login successful', 'username': account.email, 'roles': roles}))
            logger.debug('Setting cookie with token: %s', token)
            response.set_cookie('token', token, httponly=True, secure=True, samesite='Strict')

            return response, 200
        else:
            logger.debug('Invalid or expired OTP for email: %s', data['email'])
            login_attempt.failed_attempts += 1
            if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
                login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
            db.session.commit()
            return jsonify({'message': 'Invalid or expired OTP'}), 400
    except ValueError as e:
        logger.debug('Error verifying OTP for email: %s, error: %s', data['email'], str(e))
        login_attempt.failed_attempts += 1
        if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
            login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
        db.session.commit()
        return jsonify({'message': str(e)}), 400

@bp.route('/request_otp', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def request_otp():
    data = request.get_json()
    email = data.get('email')

    account = Account.query.filter_by(email=email).first()
    if not account:
        return jsonify({'error': 'Invalid email address'}), 404

    otp = generate_otp(account)
    account.otp = otp
    account.otp_generated_at = datetime.now()
    db.session.commit()

    send_otp(account, otp)
    log_audit_event(account.account_id, account.name, 'Request OTP', 'OTP requested', get_ip_address())
    return jsonify({'message': 'OTP sent to email.'}), 200

@bp.route('/verify_otp', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def verify_otp_route():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    account = Account.query.filter_by(email=email).first()
    if not account:
        return jsonify({'error': 'Invalid email address'}), 404

    if verify_otp(account, otp):
        return jsonify({'message': 'OTP verified successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid or expired OTP.'}), 400

@bp.route('/csrf-token', methods=['POST'])
def get_csrf_token():
    csrf_token = generate_csrf(secret_key=current_app.config['SECRET_KEY'])
    response = make_response(jsonify({'csrf_token': csrf_token}))
    response.set_cookie('XSRF-TOKEN', csrf_token)
    return response

@bp.route('/register', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')

    if not email or not password or not username or not date_of_birth or not address:
        return jsonify({'message': 'All fields are required'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if not validate_password(password):
        return jsonify({'message': 'Password must be at least 12 characters long, contain at least one number, and one special character'}), 400

    email = sanitize_input(email)
    username = sanitize_input(username)
    address = sanitize_input(address)
    date_of_birth = sanitize_input(date_of_birth)

    if Account.query.filter_by(email=email).first():
        return jsonify({'message': 'Account already exists'}), 400

    account = Account(
        email=email,
        password=pbkdf2_sha256.hash(password),
        name=username,
        date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
        address=address
    )

    user_role = Role.query.filter_by(name='User').first()
    if user_role:
        account.roles.append(user_role)

    now = datetime.now()
    token = generate_token(account.email)
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm?token={token}"
    send_email('Confirm Your Account', account.email, 'email/confirm', confirm_url=confirm_url)

    account.confirmation_token = token
    account.confirmation_email_sent_at = now
    db.session.add(account)
    db.session.commit()

    return jsonify({'message': 'Account registered successfully. Please check your email to confirm your account.'}), 201

from flask import Blueprint, request, jsonify, current_app
from api.auth.utils import verify_token, generate_token, send_email
from api.models import Account
from api import db
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/confirm', methods=['GET'])
@limiter.limit("5 per minute") # Apply rate limiting
def confirm_email():
    token = request.args.get('token')
    current_app.logger.debug(f"Token received: {token}")
    
    email = verify_token(token)
    current_app.logger.debug(f"Email from token: {email}")
    
    if email is False:
        current_app.logger.error("Token verification failed or expired.")
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    account = Account.query.filter_by(email=email).first_or_404()
    current_app.logger.debug(f"Account found: {account.email}")
    
    if account.confirmation_token != token:
        current_app.logger.error("Token does not match the stored token.")
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    if account.confirmed:
        current_app.logger.info("Account already confirmed.")
        return jsonify({'message': 'Account already confirmed. Please login.'}), 200
    else:
        account.confirmed = True
        account.confirmed_on = datetime.now()
        account.confirmation_token = None 
        account.confirmation_email_sent_at = None
        db.session.add(account)
        db.session.commit()
        current_app.logger.info("Account confirmed successfully.")
        return jsonify({'message': 'You have confirmed your account. Thanks!'}), 200

@bp.route('/status', methods=['GET'])
@csrf.exempt
def status():
    if current_user.is_authenticated:
        roles = [role.name for role in current_user.roles]
        return jsonify({'loggedIn': True, 'username': current_user.name, 'roles': roles}), 200
    else:
        return jsonify({'loggedIn': False}), 200

@bp.route('/logout', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('session')
    response.delete_cookie('XSRF-TOKEN')
    return response, 200

@bp.route('/refresh', methods=['POST'])
@csrf.exempt
@login_required
def refresh_token():
    try:
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        new_token = jwt.encode({
            'sub': data['sub'],
            'iat': datetime.now(),
            'exp': datetime.now() + timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        response = jsonify({'message': 'Token refreshed'})
        response.set_cookie('token', new_token, httponly=True, secure=True, samesite='Strict')


        return response
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        return jsonify({'error': str(e)}), 500
