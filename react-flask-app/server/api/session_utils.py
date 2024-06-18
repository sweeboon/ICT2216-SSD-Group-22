from functools import wraps
from flask import session, jsonify
from api.models import Sessions

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401

        # Verify session token in the database
        session_entry = Sessions.query.filter_by(token=session.sid).first()
        if not session_entry:
            session.clear()
            return jsonify({'message': 'Session expired or invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated_function