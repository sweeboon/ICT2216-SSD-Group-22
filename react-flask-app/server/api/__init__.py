from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_session import Session
from flask_security import Security, SQLAlchemyUserDatastore
from dotenv import load_dotenv
import os
from flask_mailman import Mail

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
security = Security()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    from api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    return app

# Ensure models are imported so that they are registered with SQLAlchemy
from api.models import User, Role  # Correct import path
