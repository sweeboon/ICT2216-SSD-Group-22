from flask_login import UserMixin
from flask_principal import RoleNeed, UserNeed
from api import db
from sqlalchemy import Integer, String, Boolean, DateTime, Column, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    extend_existing=True
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    last_login_at = db.Column(db.DateTime(), nullable=True)
    login_count = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime(), nullable=True)
    profiles = db.relationship('Profile', backref='user', lazy=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def get_id(self):
        return self.user_id

    def get_roles(self):
        return [role.name for role in self.roles]

    def has_role(self, role_name):
        return role_name in self.get_roles()
    

class Profile(db.Model):
    profile_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    image_id = db.Column(db.Integer)
    product_description = db.Column(db.String(255))
    product_price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    image_path = db.Column(db.String(255))