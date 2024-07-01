from flask import jsonify, request, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed, RoleNeed, Permission
from api.auth import bp
from api.models import Account, Role, Sessions
from api import db, csrf, mail
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from .utils import generate_token, verify_token
from .email import send_email
import jwt
from flask_wtf.csrf import generate_csrf
import logging
import pyotp
import secrets

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

    account.last_login_at = datetime.now()
    account.login_count += 1
    db.session.commit()

    token = jwt.encode({
        'sub': account.email,
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    login_user(account, remember=True, duration=timedelta(minutes=30))

    identity_changed.send(current_app._get_current_object(), identity=Identity(account.account_id))

    roles = [role.name for role in account.roles]

    return jsonify({'message': 'Login successful', 'token': token, 'username': account.email, 'roles': roles}), 200

@bp.route('/status', methods=['GET'])
@csrf.exempt
def status():
    if current_user.is_authenticated:
        roles = [role.name for role in current_user.roles]
        return jsonify({'loggedIn': True, 'username': current_user.name, 'roles': roles}), 200
    else:
        return jsonify({'loggedIn': False}), 200

@bp.route('/logout', methods=['POST'])
@csrf.exempt
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('session')
    response.delete_cookie('XSRF-TOKEN')
    return response, 200

@bp.route('/sessions', methods=['POST'])
def create_session():
    try:
        ssid = secrets.token_urlsafe(32)  # Generate a secure random token
        payload = {
            'ssid': ssid,
            'exp': datetime.utcnow() + timedelta(days=1)  # Set token expiry
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        new_session = Sessions(ssid=ssid, timestamp=datetime.utcnow(), token=token)
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'token': token, 'ssid': ssid}), 201
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/sessions/<ssid>', methods=['PUT'])
def update_session(ssid):
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 403
        try:
            data = jwt.decode(token.split()[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
            session = Sessions.query.get_or_404(data['ssid'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 403

        payload = request.json
        if 'timestamp' in payload:
            session.timestamp = payload['timestamp']
        if 'token' in payload:
            session.token = payload['token']
        if 'referer' in payload:
            session.referer = payload['referer']
        
        db.session.commit()
        return jsonify({'message': 'Session updated'}), 200
    except Exception as e:
        logging.error(f"Error updating session {ssid}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/sessions', methods=['GET'])
def get_session():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 403
    try:
        data = jwt.decode(token.split()[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
        session = Sessions.query.get(data['ssid'])
        if session is None:
            return jsonify({'error': 'Session not found'}), 404
        session_data = {
            'ssid': session.ssid,
            'timestamp': session.timestamp,
            'token': session.token,
            'referer': session.referer
        }
        return jsonify(session_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 403
    except Exception as e:
        logging.error(f"Error fetching session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/sessions/cleanup', methods=['POST'])
def cleanup_sessions():
    try:
        now = datetime.utcnow()
        expired_sessions = Sessions.query.filter(Sessions.timestamp < now - timedelta(days=1)).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Expired sessions cleaned up'}), 200
    except Exception as e:
        logging.error(f"Error cleaning up sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500
