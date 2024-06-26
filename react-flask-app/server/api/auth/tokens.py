from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SIGNER_SECRET_KEY'])

def generate_token(data):
    serializer = get_serializer()
    return serializer.dumps(data, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_token(token, max_age=3600):
    serializer = get_serializer()
    try:
        data = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=max_age)
    except Exception as e:
        return None
    return data