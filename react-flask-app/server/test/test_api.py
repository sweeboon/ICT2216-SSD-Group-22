import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from api.models import Account, Cart, Payment, Order, Product, Role, AuditLog
from api import create_app, db as db_instance
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app(TestConfig)
        return app

    def setUp(self):
        db_instance.create_all()

        # Add test data if necessary
        user_role = Role(name='User', description='User role')
        admin_role = Role(name='Admin', description='Admin role')
        db_instance.session.add(user_role)
        db_instance.session.add(admin_role)
        db_instance.session.commit()

    def tearDown(self):
        db_instance.session.remove()
        db_instance.drop_all()

@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestConfig)
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    
    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    db_instance.create_all()
    
    yield db_instance  # this is where the testing happens!

    db_instance.drop_all()

# Sample user data for testing
test_userdata = {
    "email": "testuser@gmail.com",
    "password": "Testing123@!",
    "username": "testname",
    "date_of_birth": "2000-01-01",
    "address": "123 Test St, Test City, Test Country"
}

# URLs for API endpoints
URL_REGISTER_USER = "/auth/register"
URL_GET_USER = "/admin/users"
URL_DELETE_USER = "/admin/users/{account_id}"
URL_LOGIN = "/auth/initiate_login"
URL_VERIFY_OTP = "/auth/verify_otp_and_login"

def test_register_user(test_client, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    assert response.status_code == 201  # Successful creation returns 201
    data = response.json
    assert 'message' in data
    assert data['message'] == 'Account registered successfully. Please check your email to confirm your account.'

def test_get_users(test_client, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    assert response.status_code == 201

    # Get users (assuming admin permission required, so we'll bypass for the test)
    response = test_client.get(URL_GET_USER)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)

def test_delete_user(test_client, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    assert response.status_code == 201

    # Get the user account_id
    response = test_client.get(URL_GET_USER)
    data = response.json
    user_id = data[0]['account_id']

    # Delete user
    response = test_client.delete(URL_DELETE_USER.format(account_id=user_id))
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert data['message'] == 'User deleted successfully'

def test_initiate_login(test_client, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    assert response.status_code == 201

    # Initiate login
    login_data = {
        "email": test_userdata['email'],
        "password": test_userdata['password']
    }
    response = test_client.post(URL_LOGIN, json=login_data)
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert data['message'] == 'OTP sent to email.'
    assert 'otp_required' in data
    assert data['otp_required'] is True

def test_verify_otp_and_login(test_client, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    assert response.status_code == 201

    # Initiate login
    login_data = {
        "email": test_userdata['email'],
        "password": test_userdata['password']
    }
    response = test_client.post(URL_LOGIN, json=login_data)
    assert response.status_code == 200

    # Here you would typically retrieve the OTP sent to the email
    # For testing purposes, we'll assume a known OTP value
    otp = "123456"

    # Verify OTP and login
    otp_data = {
        "email": test_userdata['email'],
        "otp": otp
    }
    response = test_client.post(URL_VERIFY_OTP, json=otp_data)
    assert response.status_code == 200
    data = response.json
    assert 'message' in data
    assert data['message'] == 'Login successful'
