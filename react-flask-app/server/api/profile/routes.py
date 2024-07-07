from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from api.models import Account
from api import db, csrf, limiter
import logging
from datetime import datetime
from ..auth.utils import generate_otp, verify_otp, send_otp
from api.profile import bp
from passlib.hash import pbkdf2_sha256
import html
import re

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate and sanitize input data
def validate_email(email):
    email_regex = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(email_regex, email)

def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
        return False
    return True

def sanitize_input(input):
    if input is None:
        return None
    return html.escape(input)

@bp.route('/request-otp', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def request_otp():
    try:
        data = request.get_json()
        logger.info(f"Raw data: {data}")
        change_type = sanitize_input(data.get('change_type'))
        new_email = sanitize_input(data.get('new_email'))

        logger.info(f"Sanitized change_type: {change_type}, new_email: {new_email}")

        if current_user.is_anonymous:
            return jsonify({'error': 'User not authenticated'}), 401

        if change_type == 'email':
            if not new_email:
                return jsonify({'error': 'Email is required'}), 400
            if not validate_email(new_email):
                return jsonify({'error': 'Invalid email format'}), 400
            existing_account = Account.query.filter_by(email=new_email).first()
            if existing_account:
                return jsonify({'error': 'Email already in use'}), 400
            current_user.new_email = new_email

        otp = generate_otp(current_user)
        db.session.commit()

        send_otp(current_user, otp)

        return jsonify({'message': 'OTP sent to your current email address', 'otp_required': True}), 200
    except Exception as e:
        logger.error(f'Error requesting OTP: {e}')
        return jsonify({'error': 'Failed to request OTP', 'details': str(e)}), 500

@bp.route('/verify-otp', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def verify_otp_route():
    try:
        data = request.get_json()
        logger.info(f"Raw data: {data}")
        otp = sanitize_input(data.get('otp'))
        change_type = sanitize_input(data.get('change_type'))
        new_password = sanitize_input(data.get('new_password'))
        confirm_password = sanitize_input(data.get('confirm_password'))

        logger.info(f"Sanitized otp: {otp}, change_type: {change_type}, new_password: {new_password}")

        # Verify OTP
        result = verify_otp(current_user, otp)
        if change_type == 'email':
            new_email = current_user.new_email
            current_user.email = new_email
            current_user.new_email = None
        elif change_type == 'password':
            if not validate_password(new_password):
                return jsonify({'error': 'Password must be at least 8 characters long, contain at least one number, and one special character'}), 400
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            current_user.password = pbkdf2_sha256.hash(new_password)

        db.session.commit()
        return jsonify({'message': f'{change_type.capitalize()} changed successfully'}), 200
    except Exception as e:
        logger.error(f'Error verifying OTP: {e}')
        return jsonify({'error': 'Failed to verify OTP', 'details': str(e)}), 500

@bp.route('/', methods=['GET'])
@login_required
@limiter.limit("5 per minute") # Apply rate limiting
def get_profile():
    try:
        account = current_user
        profile_data = {
            'name': account.name,
            'address': account.address,
            'date_of_birth': account.date_of_birth.strftime('%Y-%m-%d') if account.date_of_birth else None,
            'email': account.email
        }
        return jsonify(profile_data), 200
    except Exception as e:
        logger.error(f'Error fetching profile: {e}')
        return jsonify({'error': 'Failed to fetch profile'}), 500

@bp.route('/', methods=['PUT'])
@login_required
@csrf.exempt
@limiter.limit("5 per minute") # Apply rate limiting
def update_profile():
    try:
        data = request.get_json()
        logger.info(f"Raw data: {data}")
        account = current_user

        # Sanitize and validate input data
        sanitized_name = sanitize_input(data.get('name'))
        sanitized_address = sanitize_input(data.get('address'))
        sanitized_date_of_birth = sanitize_input(data.get('date_of_birth'))

        logger.info(f"Sanitized data: name={sanitized_name}, address={sanitized_address}, date_of_birth={sanitized_date_of_birth}")

        if sanitized_name:
            account.name = sanitized_name
        if sanitized_address:
            account.address = sanitized_address
        if sanitized_date_of_birth:
            try:
                account.date_of_birth = datetime.strptime(sanitized_date_of_birth, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        logger.error(f'Error updating profile: {e}')
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500
