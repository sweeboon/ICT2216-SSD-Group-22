from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mailman import Mail
from flask_wtf import CSRFProtect 
from flask_login import LoginManager, current_user
from flask_principal import Principal, Permission, PermissionDenied, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, IdentityContext

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
    CORS(app)
    csrf.init_app(app)
    principal.init_app(app)
    login_manager.init_app(app)

    from api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if hasattr(current_user, 'user_id'):
            identity.provides.add(UserNeed(current_user.user_id))
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


# Ensure models are imported so that they are registered with SQLAlchemy
from api.models import User, Role, Profile  # Correct import path
