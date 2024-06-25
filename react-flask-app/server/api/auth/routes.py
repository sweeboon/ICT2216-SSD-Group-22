from flask import jsonify, request, current_app, redirect
from flask_security import auth_required, current_user, login_user, logout_user, hash_password
from api.auth import bp
from api.models import User, Profile
from api import db, security
from datetime import datetime, timedelta
from flask_security.utils import send_mail, url_for_security, password_length_validator, password_complexity_validator, verify_and_update_password, check_and_get_token_status

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if user already exists
    if security.datastore.find_user(email=data['email']):
        return jsonify({'message': 'User already exists'}), 400

    # Validate password length
    password_errors = password_length_validator(data['password'])
    if password_errors:
        return jsonify({'message': 'Password does not meet length requirements', 'errors': password_errors}), 400

    # Validate password complexity
    complexity_errors = password_complexity_validator(data['password'], is_register=True, email=data['email'], username=data['username'])
    if complexity_errors:
        return jsonify({'message': 'Password does not meet complexity requirements', 'errors': complexity_errors}), 400

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

    # Generate the confirmation token
    token = user.get_auth_token()
    print(f"Generated Token: {token}")

    # Construct the confirmation link
    frontend_base_url = current_app.config['FRONTEND_BASE_URL']
    confirmation_link = f"{frontend_base_url}/confirm?token={token}"
    print(f"Confirmation Link: {confirmation_link}")

    # Send the confirmation email
    send_mail('Please confirm your email address', user.email, 'confirmation_instructions', user=user, confirmation_link=confirmation_link)

    return jsonify({'message': 'User and profile registered successfully. Please check your email to confirm your account.'}), 201

@bp.route('/confirm', methods=['GET'])
def confirm_email():
    token = request.args.get('token')
    print(f"Received Token: {token}")
    try:
        expired, invalid, user = check_and_get_token_status(token, 'confirm', within=timedelta(days=1))
        print(f"Token Status - Expired: {expired}, Invalid: {invalid}, User: {user}")
    except Exception as e:
        print(f"Token Validation Error: {e}")
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400
    
    if invalid or expired:
        status = 'invalid' if invalid else 'expired'
    else:
        user.confirmed_at = datetime.now()
        db.session.commit()
        status = 'success'

    frontend_base_url = current_app.config['FRONTEND_BASE_URL']
    return redirect(f"{frontend_base_url}/confirmation-result?status={status}")


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400
    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user is None or not verify_and_update_password(data['password'], user):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Log in the user
    login_user(user)
    security.datastore.commit()
    return jsonify({'message': 'Login successful', 'logged_in_as': user.email}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200
