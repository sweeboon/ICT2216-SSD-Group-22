from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from api.models import Account
from api import db, csrf
import logging
from datetime import datetime
from ..auth.utils import generate_otp, verify_otp, send_otp
from api.profile import bp
from passlib.hash import pbkdf2_sha256

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/request-otp', methods=['POST'])
@login_required
@csrf.exempt
def request_otp():
    try:
        data = request.get_json()
        change_type = data.get('change_type')
        new_email = data.get('new_email', None)

        otp = generate_otp()

        # Integrate store_otp functionality here
        if current_user.is_anonymous:
            return jsonify({'error': 'User not authenticated'}), 401

        if change_type == 'email':
            if not new_email:
                return jsonify({'error': 'Email is required'}), 400
            existing_account = Account.query.filter_by(email=new_email).first()
            if existing_account:
                return jsonify({'error': 'Email already in use'}), 400
            current_user.new_email = new_email

        # Store OTP and timestamp in the user's record
        current_user.otp = otp
        current_user.otp_generated_at = datetime.now()
        db.session.commit()

        send_otp(current_user, otp)

        return jsonify({'message': 'OTP sent to your current email address', 'otp_required': True}), 200
    except Exception as e:
        logger.error(f'Error requesting OTP: {e}')
        return jsonify({'error': 'Failed to request OTP', 'details': str(e)}), 500

@bp.route('/verify-otp', methods=['POST'])
@login_required
@csrf.exempt
def verify_otp_route():
    try:
        data = request.get_json()
        otp = data.get('otp')
        change_type = data.get('change_type')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Verify OTP
        result = verify_otp(current_user, otp)
        if change_type == 'email':
            new_email = current_user.new_email
            current_user.email = new_email
            current_user.new_email = None
        elif change_type == 'password':
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
def update_profile():
    try:
        data = request.get_json()
        account = current_user

        if 'email' in data or 'password' in data:
            return jsonify({'error': 'OTP is required to change email or password'}), 400

        if 'name' in data:
            account.name = data['name']
        if 'address' in data:
            account.address = data['address']
        if 'date_of_birth' in data:
            account.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        logger.error(f'Error updating profile: {e}')
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500
