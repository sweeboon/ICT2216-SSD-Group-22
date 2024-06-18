from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from api import db
from werkzeug.security import generate_password_hash, check_password_hash

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    role = db.Column(db.String(255), db.ForeignKey('permission.role'), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Account {self.name}>'
    

class Permission(db.Model):
    role = db.Column(db.String(255), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    permissions = db.Column(db.JSON)

    def __repr__(self):
        return f'<Permission {self.role}>'
