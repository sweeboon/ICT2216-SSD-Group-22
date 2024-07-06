from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import Account, Role, LoginAttempt
from api import db, csrf, limiter
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .utils import generate_token, verify_token, generate_otp, send_otp, verify_otp, send_email
import jwt
from flask_wtf.csrf import generate_csrf
import logging
import pyotp
import secrets
import bleach, re

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15)

def validate_email(email):
    email_regex = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(email_regex, email)

def sanitize_input(input):
    return bleach.clean(input, strip=True)

def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
        return False
    return True

@bp.route('/reset_password_request', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
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

    return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200

@bp.route('/reset_password', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
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
        return jsonify({'error': 'Password must be at least 8 characters long, contain at least one number, and one special character'}), 400

    account.password = pbkdf2_sha256.hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password reset successful'}), 200

@bp.route('/resend_confirmation_email', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
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
        return jsonify({'message': 'Confirmation email already sent. Please wait a minute before requesting a new one.'}), 400

    token = generate_token(account.email)
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm?token={token}"
    send_email('Confirm Your Account', account.email, 'email/confirm', confirm_url=confirm_url)

    account.confirmation_token = token  
    account.confirmation_email_sent_at = now  
    db.session.commit()

    return jsonify({'message': 'Confirmation email sent. Please check your email.'}), 200

@bp.route('/initiate_login', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def initiate_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    email = sanitize_input(email)
    password = sanitize_input(password)

    account = Account.query.filter_by(email=email).first()
    if account is None:
        return jsonify({'message': 'Invalid email or password'}), 401

    if not account.confirmed:
        return jsonify({
            'message': 'Account not confirmed. Do you want to resend the confirmation email?',
            'resend_confirmation': True
        }), 403

    login_attempt = LoginAttempt.query.filter_by(account_id=account.account_id).first()
    if not login_attempt:
        login_attempt = LoginAttempt(account_id=account.account_id)
        db.session.add(login_attempt)
        db.session.commit()

    if login_attempt.lockout_time and datetime.now() < login_attempt.lockout_time:
        return jsonify({'message': 'Account is locked. Please try again later.'}), 403

    if not pbkdf2_sha256.verify(password, account.password):
        login_attempt.failed_attempts += 1
        if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
            login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
        db.session.commit()
        return jsonify({'message': 'Invalid email or password'}), 401

    login_attempt.failed_attempts = 0
    db.session.commit()

    otp = generate_otp(account)
    send_otp(account, otp)
    return jsonify({'message': 'OTP sent to email.', 'otp_required': True}), 200

@bp.route('/verify_otp_and_login', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def verify_otp_and_login():
    data = request.get_json()
    if 'email' not in data or 'otp' not in data:
        return jsonify({'message': 'Email and OTP are required'}), 400

    account = Account.query.filter_by(email=data['email']).first()
    if account is None:
        return jsonify({'message': 'Invalid email address'}), 401

    login_attempt = LoginAttempt.query.filter_by(account_id=account.account_id).first()
    if login_attempt.lockout_time and datetime.now() < login_attempt.lockout_time:
        return jsonify({'message': 'Account is locked. Please try again later.'}), 403

    try:
        if verify_otp(account, data['otp']):
            login_attempt.failed_attempts = 0
            login_attempt.lockout_time = None
            login_attempt.last_login_at = datetime.now()
            login_attempt.login_count += 1
            db.session.commit()

            token = jwt.encode({
                'sub': account.email,
                'iat': datetime.now(),
                'exp': datetime.now() + timedelta(minutes=30)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            login_user(account, remember=True, duration=timedelta(minutes=30))
            identity_changed.send(current_app._get_current_object(), identity=Identity(account.account_id))
            roles = [role.name for role in account.roles]

            response = make_response(jsonify({'message': 'Login successful', 'username': account.email, 'roles': roles}))
            response.set_cookie('token', token, httponly=True, secure=True, samesite='Strict')
            return response, 200
        else:
            login_attempt.failed_attempts += 1
            if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
                login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
            db.session.commit()
            return jsonify({'message': 'Invalid or expired OTP'}), 400
    except ValueError as e:
        login_attempt.failed_attempts += 1
        if login_attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
            login_attempt.lockout_time = datetime.now() + LOCKOUT_TIME
        db.session.commit()
        return jsonify({'message': str(e)}), 400

@bp.route('/request_otp', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
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
    return jsonify({'message': 'OTP sent to email.'}), 200

@bp.route('/verify_otp', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
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
@limiter.limit("10 per minute")
def get_csrf_token():
    csrf_token = generate_csrf(secret_key=current_app.config['SECRET_KEY'])
    response = make_response(jsonify({'csrf_token': csrf_token}))
    response.set_cookie('XSRF-TOKEN', csrf_token)
    return response

@bp.route('/register', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
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
        return jsonify({'message': 'Password must be at least 8 characters long, contain at least one number, and one special character'}), 400

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

@bp.route('/confirm', methods=['GET'])
@limiter.limit("5 per minute")
def confirm_email():
    token = request.args.get('token')
    email = verify_token(token)
    if email is False:
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    account = Account.query.filter_by(email=email).first_or_404()
    if account.confirmation_token != token:
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    if account.confirmed:
        return jsonify({'message': 'Account already confirmed. Please login.'}), 200
    else:
        account.confirmed = True
        account.confirmed_on = datetime.now()
        account.confirmation_token = None 
        account.confirmation_email_sent_at = None
        db.session.add(account)
        db.session.commit()
        return jsonify({'message': 'You have confirmed your account. Thanks!'}), 200

@bp.route('/status', methods=['GET'])
@csrf.exempt
@limiter.limit("10 per minute")
def status():
    if current_user.is_authenticated:
        roles = [role.name for role in current_user.roles]
        return jsonify({'loggedIn': True, 'username': current_user.name, 'roles': roles}), 200
    else:
        return jsonify({'loggedIn': False}), 200

@bp.route('/logout', methods=['POST'])
@csrf.exempt
@login_required
@limiter.limit("10 per minute")
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('session')
    response.delete_cookie('XSRF-TOKEN')
    return response, 200
