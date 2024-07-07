from flask import Flask, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mailman import Mail
from flask_wtf import CSRFProtect
from flask_login import LoginManager, current_user
from flask_principal import Principal, RoleNeed, UserNeed, identity_loaded, Identity, AnonymousIdentity, IdentityContext
import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
principal = Principal()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    principal.init_app(app)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

    app.supabase = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

    from api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    from api.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')

    from api.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if hasattr(current_user, 'account_id'):
            identity.provides.add(UserNeed(current_user.account_id))
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @login_manager.user_loader
    def load_user(account_id):
        return Account.query.get(int(account_id))

    @login_manager.request_loader
    def load_user_from_request(request):
        auth_headers = request.headers.get('Authorization', '').split()
        if len(auth_headers) != 2:
            return None
        try:
            token = auth_headers[1]
            print(token)
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            account = Account.query.filter_by(email=data['sub']).first()
            if account:
                return account
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidTokenError, Exception):
            return None
        return None
    
    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            headers = None
            if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
                headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']
            response.headers['Access-Control-Allow-Headers'] = headers or '*'
            return response

    return app

# Ensure models are imported so that they are registered with SQLAlchemy
from api.models import Account, Role
