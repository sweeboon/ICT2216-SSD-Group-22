from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
sess = Session()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SESSION_SQLALCHEMY'] = db
    sess.init_app(app)
    csrf.init_app(app)

    from api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    return app

from api import models