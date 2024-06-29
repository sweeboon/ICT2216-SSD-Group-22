from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import User, Profile, Role
from api import db, csrf, mail
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .tokens import generate_token, verify_token
from .email import send_email
import jwt
from flask_wtf.csrf import generate_csrf
from api.auth.email import send_otp_email
import logging
import pyotp


super_admin_permission = Permission(RoleNeed('SuperAdmin'))
admin_permission = Permission(RoleNeed('Admin'))
logger = logging.getLogger(__name__)

@bp.route('/csrf-token', methods=['POST'])
def get_csrf_token():
    csrf_token = generate_csrf(secret_key=current_app.config['SECRET_KEY'])
    response = make_response(jsonify({'csrf_token': csrf_token}))
    response.set_cookie('XSRF-TOKEN', csrf_token)
    return response

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(
        email=data['email'],
        password=pbkdf2_sha256.hash(data['password']),
    )

    user_role = Role.query.filter_by(name='User').first()
    if user_role:
        user.roles.append(user_role)

    date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None
    profile = Profile(
        name=data['username'],
        date_of_birth=date_of_birth,
        address=data.get('address'),
        user=user
    )

    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    token = generate_token(user.email)
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm?token={token}"
    send_email('Confirm Your Account', user.email, 'email/confirm', confirm_url=confirm_url)
    print(confirm_url)
    return jsonify({'message': 'User and profile registered successfully. Please check your email to confirm your account.'}), 201

@bp.route('/confirm', methods=['GET'])
def confirm_email():
    token = request.args.get('token')
    email = verify_token(token, 1800)
    if email is None:
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        return jsonify({'message': 'Account already confirmed. Please login.'}), 200
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'You have confirmed your account. Thanks!'}), 200

@bp.route('/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400
    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user is None or not pbkdf2_sha256.verify(data['password'], user.password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Update login timestamps and count
    user.last_login_at = datetime.now()
    user.login_count += 1

    # Save the user data
    db.session.commit()

    # Generate JWT token
    token = jwt.encode({
        'sub': user.email,
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    # Log in the user
    login_user(user, remember=True, duration=timedelta(minutes=30))

    # Notify Flask-Principal of the login
    identity_changed.send(current_app._get_current_object(), identity=Identity(user.user_id))

    return jsonify({'message': 'Login successful', 'token': token, 'username': user.email}), 200


@bp.route('/logout', methods=['POST'])
@csrf.exempt
@login_required
def logout():
    # Log out the user
    logout_user()

    # Remove user identity
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    # Clear the cookies
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('session')
    response.delete_cookie('XSRF-TOKEN')
    
    return response, 200


@bp.route('/status', methods=['GET'])
@csrf.exempt
def status():
    if current_user.is_authenticated:
        profile = Profile.query.filter_by(user_id=current_user.user_id).first()
        return jsonify({'loggedIn': True, 'username': profile.name}), 200
    else:
        return jsonify({'loggedIn': False}), 200

# Endpoint to get all users except the current user
@bp.route('/users', methods=['GET'])
@login_required
@super_admin_permission.require(http_exception=403)
def get_users():
    users = User.query.filter(User.user_id != current_user.user_id).all()
    users_data = [{'user_id': user.user_id, 'email': user.email, 'roles': [role.name for role in user.roles]} for user in users]
    return jsonify(users_data), 200

@bp.route('/assign-role', methods=['POST'])
@login_required
@super_admin_permission.require(http_exception=403)
def assign_role():
    data = request.get_json()
    user_id = data.get('user_id')
    role_name = data.get('role_name')

    if not user_id or not role_name:
        return jsonify({'message': 'User ID and Role Name are required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Prevent current user from changing their own roles
    if user.user_id == current_user.user_id:
        return jsonify({'message': 'You cannot change your own roles'}), 403

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    # Clear existing roles
    user.roles = []

    # Assign new role
    user.roles.append(role)
    db.session.commit()

    return jsonify({'message': f'Role {role_name} assigned to user {user.email} successfully'}), 200

@bp.route('/roles', methods=['GET'])
@login_required
@super_admin_permission.require(http_exception=403)
def get_roles():
    roles = Role.query.all()
    roles_data = [{'id': role.id, 'name': role.name} for role in roles]
    return jsonify(roles_data), 200

@bp.route('/request-email-change', methods=['POST'])
@login_required
def request_email_change():
    try:
        data = request.get_json()
        new_email = data.get('email')

        if not new_email:
            return jsonify({'error': 'Email is required'}), 400

        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user:
            return jsonify({'error': 'Email already in use'}), 400

        # Generate OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        otp = totp.now()

        # Store the OTP and timestamp in the user's session (or a more secure storage)
        current_user.otp = otp
        current_user.otp_generated_at = datetime.now()
        current_user.new_email = new_email
        db.session.commit()

        # Send OTP email to the old email address
        send_otp_email(current_user.email, otp)

        return jsonify({'message': 'OTP sent to your current email address'}), 200
    except Exception as e:
        logger.error(f'Error requesting email change: {e}')
        return jsonify({'error': 'Failed to request email change', 'details': str(e)}), 500

@bp.route('/verify-email-change', methods=['POST'])
@login_required
def verify_email_change():
    try:
        data = request.get_json()
        otp = data.get('otp')

        if not otp:
            return jsonify({'error': 'OTP is required'}), 400

        # Check if the OTP is expired
        otp_generated_at = current_user.otp_generated_at
        if not otp_generated_at or (datetime.datetime.now() - otp_generated_at).total_seconds() > 300:
            return jsonify({'error': 'OTP has expired'}), 400

        # Verify OTP
        totp = pyotp.TOTP(current_app.config['SECRET_KEY'], interval=300)
        if not totp.verify(otp):
            return jsonify({'error': 'Invalid OTP'}), 400

        # Set a flag or return success so the email change can proceed
        return jsonify({'message': 'OTP verified successfully'}), 200
    except Exception as e:
        logger.error(f'Error verifying email change: {e}')
        return jsonify({'error': 'Failed to verify email change', 'details': str(e)}), 500