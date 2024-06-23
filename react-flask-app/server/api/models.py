from flask_security import UserMixin, RoleMixin
from api import db
from sqlalchemy import Integer, String, Boolean, DateTime, Column, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.types import UnicodeText

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    extend_existing = True
)

class Role(db.Model,RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    profiles = db.relationship('Profile', backref='user', lazy=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class Profile(db.Model):
    profile_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


