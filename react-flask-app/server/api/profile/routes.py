from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import current_user, login_required
from api.models import User, Role
from api import db, csrf
from passlib.hash import pbkdf2_sha256
import logging
from datetime import datetime 
import pyotp
from api.profile import bp
import requests

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@login_required
def get_profile():
    try:
        user = current_user
        profile_data = {
            'name': user.name,
            'address': user.address,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
            'email': user.email
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
        user = current_user
        otp_required = False

        if 'name' in data:
            user.name = data['name']
        if 'address' in data:
            user.address = data['address']
        if 'date_of_birth' in data:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        if 'email' in data:
            new_email = data['email']
            if new_email != user.email:
                otp_required = True
                # Request OTP for email change
                response = requests.post(url_for('auth.generate_otp', _external=True), json={'change_type': 'email', 'email': new_email})
                if response.status_code != 200:
                    return jsonify(response.json()), response.status_code
        if 'password' in data:
            new_password = data['password']
            confirm_password = data.get('confirm_password')
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            otp_required = True
            # Request OTP for password change
            response = requests.post(url_for('auth.generate_otp', _external=True), json={'change_type': 'password'})
            if response.status_code != 200:
                return jsonify(response.json()), response.status_code

        if otp_required:
            return jsonify({'message': 'OTP sent to your current email address', 'otp_required': True}), 200
        else:
            db.session.commit()
            return jsonify({'message': 'Profile updated successfully', 'otp_required': False}), 200
    except Exception as e:
        logger.error(f'Error updating profile: {e}')
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500