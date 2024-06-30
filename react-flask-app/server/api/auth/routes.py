from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import User, Role
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
        name=data['username'],  
        date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,  # Add date_of_birth field
        address=data.get('address') 
    )

    user_role = Role.query.filter_by(name='User').first()
    if user_role:
        user.roles.append(user_role)

    db.session.add(user)
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
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user is None or not pbkdf2_sha256.verify(data['password'], user.password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Update login timestamps and count
    user.last_login_at = datetime.now()
    user.login_count += 1
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
        return jsonify({'loggedIn': True, 'username': current_user.name}), 200
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

@bp.route('/generate-otp', methods=['POST'])
@csrf.exempt
def generate_otp():
    try:
        data = request.get_json()
        change_type = data.get('change_type')
        if change_type not in ['email', 'password']:
            return jsonify({'error': 'Invalid change type'}), 400

        if change_type == 'email':
            new_email = data.get('email')
            if not new_email:
                return jsonify({'error': 'Email is required'}), 400
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return jsonify({'error': 'Email already in use'}), 400
            current_user.new_email = new_email

        # Generate OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        otp = totp.now()

        # Store OTP and timestamp in the user's record
        current_user.otp = otp
        current_user.otp_generated_at = datetime.now()
        db.session.commit()

        # Send OTP email
        send_otp_email(current_user.email, otp)

        return jsonify({'message': 'OTP sent to your current email address', 'otp_required': True}), 200
    except Exception as e:
        logger.error(f'Error generating OTP: {e}')
        return jsonify({'error': 'Failed to generate OTP', 'details': str(e)}), 500

@bp.route('/verify-otp', methods=['POST'])
@csrf.exempt
def verify_otp():
    try:
        data = request.get_json()
        otp = data.get('otp')
        change_type = data.get('change_type')

        if not otp or not change_type:
            return jsonify({'error': 'OTP and change type are required'}), 400

        if change_type not in ['email', 'password']:
            return jsonify({'error': 'Invalid change type'}), 400

        # Verify OTP
        totp = pyotp.TOTP(current_app.config['OTP_SECRET_KEY'], interval=300)
        if not totp.verify(otp):
            return jsonify({'error': 'Invalid or expired OTP'}), 400

        if change_type == 'email':
            new_email = current_user.new_email
            current_user.email = new_email
            current_user.new_email = None
        elif change_type == 'password':
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            current_user.password = pbkdf2_sha256.hash(new_password)

        current_user.otp = None  # Clear OTP
        db.session.commit()

        return jsonify({'message': f'{change_type.capitalize()} changed successfully'}), 200
    except Exception as e:
        logger.error(f'Error verifying OTP: {e}')
        return jsonify({'error': f'Failed to change {change_type}', 'details': str(e)}), 500