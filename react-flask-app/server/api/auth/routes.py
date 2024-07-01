from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import Account, Role
from api import db, csrf, mail
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .utils import generate_token, verify_token
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

    if Account.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Account already exists'}), 400

    account = Account(
        email=data['email'],
        password=pbkdf2_sha256.hash(data['password']),
        name=data['username'],  
        date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
        address=data.get('address') 
    )

    user_role = Role.query.filter_by(name='User').first()
    if user_role:
        account.roles.append(user_role)

    db.session.add(account)
    db.session.commit()

    token = generate_token(account.email)
    confirm_url = f"{current_app.config['FRONTEND_BASE_URL']}/confirm?token={token}"
    send_email('Confirm Your Account', account.email, 'email/confirm', confirm_url=confirm_url)
    print(confirm_url)
    return jsonify({'message': 'Account and profile registered successfully. Please check your email to confirm your account.'}), 201

@bp.route('/confirm', methods=['GET'])
def confirm_email():
    token = request.args.get('token')
    email = verify_token(token, 1800)
    if email is None:
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

    account = Account.query.filter_by(email=email).first_or_404()
    if account.confirmed:
        return jsonify({'message': 'Account already confirmed. Please login.'}), 200
    else:
        account.confirmed = True
        account.confirmed_on = datetime.now()
        db.session.add(account)
        db.session.commit()
        return jsonify({'message': 'You have confirmed your account. Thanks!'}), 200

@bp.route('/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'}), 400

    account = Account.query.filter_by(email=data['email']).first()
    if account is None or not pbkdf2_sha256.verify(data['password'], account.password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Update login timestamps and count
    account.last_login_at = datetime.now()
    account.login_count += 1
    db.session.commit()

    # Generate JWT token
    token = jwt.encode({
        'sub': account.email,
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    # Log in the account
    login_user(account, remember=True, duration=timedelta(minutes=30))

    # Notify Flask-Principal of the login
    identity_changed.send(current_app._get_current_object(), identity=Identity(account.account_id))

    return jsonify({'message': 'Login successful', 'token': token, 'username': account.email}), 200

@bp.route('/logout', methods=['POST'])
@csrf.exempt
@login_required
def logout():
    # Log out the account
    logout_user()

    # Remove account identity
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
    users = Account.query.filter(Account.account_id != current_user.account_id).all()
    users_data = [{'account_id': user.account_id, 'email': user.email, 'roles': [role.name for role in user.roles]} for user in users]
    return jsonify(users_data), 200

@bp.route('/assign-role', methods=['POST'])
@login_required
@super_admin_permission.require(http_exception=403)
def assign_role():
    data = request.get_json()
    account_id = data.get('account_id')
    role_name = data.get('role_name')

    if not account_id or not role_name:
        return jsonify({'message': 'Account ID and Role Name are required'}), 400

    account = Account.query.get(account_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    # Prevent current user from changing their own roles
    if account.account_id == current_user.account_id:
        return jsonify({'message': 'You cannot change your own roles'}), 403

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    # Clear existing roles
    account.roles = []

    # Assign new role
    account.roles.append(role)
    db.session.commit()

    return jsonify({'message': f'Role {role_name} assigned to account {account.email} successfully'}), 200

@bp.route('/roles', methods=['GET'])
@login_required
@super_admin_permission.require(http_exception=403)
def get_roles():
    roles = Role.query.all()
    roles_data = [{'id': role.id, 'name': role.name} for role in roles]
    return jsonify(roles_data), 200
