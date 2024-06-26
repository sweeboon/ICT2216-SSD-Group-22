from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from api.models import User, Profile
from api import db
from passlib.hash import pbkdf2_sha256
import logging
from api.profile import bp

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
        }
        return jsonify(profile_data), 200
    except Exception as e:
        logger.error(f'Error fetching profile: {e}')
        return jsonify({'error': 'Failed to fetch profile'}), 500

@bp.route('/', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        profile = Profile.query.filter_by(user_id=current_user.user_id).first()

        if 'name' in data:
            profile.name = data['name']
        if 'address' in data:
            profile.address = data['address']
        if 'password' in data:
            current_user.password = pbkdf2_sha256.hash(data['password'])

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        logger.error(f'Error updating profile: {e}')
        return jsonify({'error': 'Failed to update profile'}), 500
