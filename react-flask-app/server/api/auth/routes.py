from flask import jsonify, request, session
from api.auth import bp
from api.models import Account
from api import db
from datetime import datetime
from api.session_utils import login_required

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if account already exists
    if Account.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Account already exists'}), 400
    
    date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None
    
    # Create a new account
    account = Account(
        name=data['username'],
        email=data['email'],
        date_of_birth=date_of_birth,
        address=data.get('address'),
        role=data.get('role')  # Uncomment if role is needed
    )
    account.set_password(data['password'])
    
    # Save the account to the database
    db.session.add(account)
    db.session.commit()
    
    return jsonify({'message': 'Account registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)  # Debugging print statement to see the received data
    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400
    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

    account = Account.query.filter_by(email=data['email']).first()
    if account is None or not account.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Create a session for the user
    session['user_id'] = account.account_id
    session['email'] = account.email
    session['role'] = account.role
    session.permanent = True  

    return jsonify({'message': 'Login successful'}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        session.clear()
    
    return jsonify({'message': 'Logout successful'}), 200

@bp.route('/protected', methods=['GET'])
@login_required
def protected():
    current_user = session['email']
    return jsonify(logged_in_as=current_user), 200
