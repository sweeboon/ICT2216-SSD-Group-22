from flask import jsonify, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import User, Profile, Role
from api import db, csrf
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .tokens import generate_token, verify_token
from .email import send_email

super_admin_permission = Permission(RoleNeed('SuperAdmin'))
admin_permission = Permission(RoleNeed('Admin'))

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    # Create a new user
    user = User(
        email=data['email'],
        password=pbkdf2_sha256.hash(data['password']),
    )

    # Assign default role
    user_role = Role.query.filter_by(name='User').first()
    if user_role:
        user.roles.append(user_role)

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

    token = generate_token([user.email, user.user_id])
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm/{token}"
    send_email('Confirm Your Account', user.email, 'email/confirm', confirm_url=confirm_url)

    return jsonify({'message': 'User and profile registered successfully.'}), 201

@bp.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
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
    user.last_login_at = user.current_login_at
    user.current_login_at = datetime.now()
    user.login_count += 1

    # Save the user data
    db.session.commit()

    # Log in the user
    login_user(user, remember=True, duration=timedelta(minutes=30))

    # Notify Flask-Principal of the login
    identity_changed.send(current_app._get_current_object(), identity=Identity(user.user_id))

    return jsonify({'message': 'Login successful', 'logged_in_as': user.email}), 200

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

    return jsonify({'message': 'Logout successful'}), 200

@bp.route('/status', methods=['GET'])
@csrf.exempt
def status():
    if current_user.is_authenticated:
        return jsonify({'loggedIn': True, 'username': current_user.email, 'roles': current_user.get_roles()}), 200
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
