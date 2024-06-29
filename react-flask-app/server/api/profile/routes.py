from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from api.models import User, Profile
from api import db, csrf
from passlib.hash import pbkdf2_sha256
import logging
from api.profile import bp
from datetime import datetime 
import pyotp

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@login_required
def get_profile():
    try:
        profile = Profile.query.filter_by(user_id=current_user.user_id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        profile_data = {
            'name': profile.name,
            'address': profile.address,
            'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else None,
            'email': current_user.email
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
        profile = Profile.query.filter_by(user_id=current_user.user_id).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        if 'name' in data:
            profile.name = data['name']
        if 'address' in data:
            profile.address = data['address']
        if 'date_of_birth' in data:
            profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        if 'password' in data:
            current_user.password = pbkdf2_sha256.hash(data['password'])

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        logger.error(f'Error updating profile: {e}')
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@bp.route('/change-email', methods=['POST'])
@login_required
@csrf.exempt
def change_email():
    try:
        data = request.get_json()
        otp = data.get('otp')

        if not otp:
            return jsonify({'error': 'OTP is required'}), 400

        # Verify OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        if not totp.verify(otp):
            return jsonify({'error': 'Invalid or expired OTP'}), 400

        new_email = current_user.new_email
        current_user.email = new_email
        current_user.new_email = None
        current_user.otp = None
        db.session.commit()

        return jsonify({'message': 'Email updated successfully'}), 200
    except Exception as e:
        logger.error(f'Error changing email: {e}')
        return jsonify({'error': 'Failed to change email', 'details': str(e)}), 500