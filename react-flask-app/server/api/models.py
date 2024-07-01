from flask_login import UserMixin
from flask_principal import RoleNeed, UserNeed
from flask_sqlalchemy import SQLAlchemy
from api import db
from datetime import datetime

roles_accounts = db.Table('roles_accounts',
    db.Column('account_id', db.Integer, db.ForeignKey('account.account_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    extend_existing=True
)

class Sessions(db.Model):
    ssid = db.Column(db.String(255), primary_key=True)
    timestamp = db.Column(db.DateTime())
    token = db.Column(db.String(255), nullable=True)
    referer = db.Column(db.String(255), nullable=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Account(UserMixin, db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    last_login_at = db.Column(db.DateTime(), nullable=True)
    login_count = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime(), nullable=True)
    otp = db.Column(db.String(6), nullable=True)  
    otp_generated_at = db.Column(db.DateTime(), nullable=True)  
    new_email = db.Column(db.String(255), nullable=True)  
    name = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_accounts, backref=db.backref('accounts', lazy=True))
    twofa_enabled = db.Column(db.Boolean, default=False)
    carts = db.relationship('Cart', backref='account', lazy=True)
    payments = db.relationship('Payment', backref='account', lazy=True)
    orders = db.relationship('Order', backref='account', lazy=True)

    def get_id(self):
        return self.account_id

    def get_roles(self):
        return [role.name for role in self.roles]

    def has_role(self, role_name):
        return role_name in self.get_roles()

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
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
    session_id = db.Column(db.String(255))

    # Relationships
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
