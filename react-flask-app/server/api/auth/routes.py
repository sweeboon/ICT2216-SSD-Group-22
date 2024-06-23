from flask import jsonify, request
from flask_security import auth_required, current_user, login_user, logout_user, hash_password
from api.auth import bp
from api.models import User, Profile
from api import db, security 
from datetime import datetime

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if security.datastore.find_user(email=data['email']):
        return jsonify({'message': 'User already exists'}), 400
    
    # Create a new user using user_datastore
    user = security.datastore.create_user(
        email=data['email'],
        password=hash_password(data['password']),
    )
    
    # Create a profile
    date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None
    profile = Profile(
        name=data['username'],
        date_of_birth=date_of_birth,
        address=data.get('address'),
        user=user
    )
    
    # Save the user and profile to the database
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({'message': 'User and profile registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)  # Debugging print statement to see the received data
    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400
    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user is None or not user.verify_and_update_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Log in the user
    login_user(user)

    return jsonify({'message': 'Login successful'}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@bp.route('/protected', methods=['GET'])
@auth_required()
def protected():
    return jsonify(logged_in_as=current_user.email), 200
