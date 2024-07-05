from flask_login import UserMixin
from flask_principal import RoleNeed, UserNeed
from flask_sqlalchemy import SQLAlchemy
from api import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

roles_accounts = db.Table('roles_accounts',
    db.Column('account_id', db.Integer, db.ForeignKey('account.account_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    extend_existing=True
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Account(UserMixin, db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime(), nullable=True)
    name = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))  # Address field added back
    confirmation_email_sent_at = db.Column(db.DateTime(), nullable=True)
    confirmation_token = db.Column(db.String(255), nullable=True)
    roles = db.relationship('Role', secondary=roles_accounts, backref=db.backref('accounts', lazy=True))
    carts = db.relationship('Cart', backref='account', lazy=True)
    payments = db.relationship('Payment', backref='account', lazy=True)
    orders = db.relationship('Order', backref='account', lazy=True)
    login_attempts = db.relationship('LoginAttempt', backref='login_attempt', lazy=True)
    otps = db.relationship('OTP', backref='otp_account', lazy=True)

    def get_id(self):
        return self.account_id

    def get_roles(self):
        return [role.name for role in self.roles]

    def has_role(self, role_name):
        return role_name in self.get_roles()

class LoginAttempt(db.Model):
    attempt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    lockout_time = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)

class OTP(db.Model):
    otp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    otp_generated_at = db.Column(db.DateTime(), nullable=True)
    otp_secret_key = db.Column(db.String(32), nullable=True)

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    product_description = db.Column(db.String(255))
    product_price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    image_path = db.Column(db.String(255))
    orders = db.relationship('Order', backref='product', lazy=True)

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    quantity = db.Column(db.Integer)
    cart_item_price = db.Column(db.Float)
    product = db.relationship("Product", backref="cart", lazy=True)

class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    total_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(255))
    payment_status = db.Column(db.String(255))
    payment_date = db.Column(db.DateTime(), default=datetime.now)
    orders = db.relationship('Order', backref='payment', lazy=True)

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    order_status = db.Column(db.String(255))
    order_price = db.Column(db.Float)
    order_date = db.Column(db.DateTime(), default=datetime.now)
    quantity = db.Column(db.Integer)

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(255), nullable = False)

