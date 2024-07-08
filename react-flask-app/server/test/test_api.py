import pytest
from api.models import Account, OTP
from api.auth.utils import generate_token
from api import db
import logging

# Setup URLs for API endpoints
URL_REGISTER_USER = '/auth/register'
URL_CONFIRM_EMAIL = '/auth/confirm'
URL_INITIATE_LOGIN = '/auth/initiate_login'
URL_VERIFY_OTP_AND_LOGIN = '/auth/verify_otp_and_login'

# Test user data
test_userdata = {
    "email": "testuser@example.com",
    "password": "Password123!",
    "username": "testuser",
    "date_of_birth": "2000-01-01",
    "address": "123 Test Street"
}

def confirm_account(client, email):
    account = Account.query.filter_by(email=email).first()
    if not account:
        raise ValueError(f"Account with email {email} not found")
    
    token = generate_token(email)
    account.confirmation_token = token
    db.session.commit()

    response = client.get(f"{URL_CONFIRM_EMAIL}?token={token}")
    logging.debug(f"Confirm URL response: {response.status_code}, {response.data}")
    assert response.status_code == 200, f"Failed to confirm account: {response.data}"

def test_register_user(client, init_database):
    logging.debug(f"Test user data: {test_userdata}")
    response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Register response: {response.status_code}, {response.data}")
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}, {response.data}"

def test_initiate_login(client, init_database):
    logging.debug(f"Test user data: {test_userdata}")
    # Register user
    register_response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Register response: {register_response.status_code}, {register_response.data}")
    assert register_response.status_code == 201, f"Registration failed: {register_response.status_code}, {register_response.data}"

    # Confirm the account
    confirm_account(client, test_userdata['email'])

    # Initiate login with the newly registered user
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    assert response.status_code == 200, f"Login failed: {response.status_code}, {response.data}"

    # Retrieve the OTP sent
    account = Account.query.filter_by(email=test_userdata['email']).first()
    otp_record = OTP.query.filter_by(account_id=account.account_id).first()
    otp = otp_record.otp

    # Verify the OTP
    otp_data = {
        "email": test_userdata["email"],
        "otp": otp
    }
    response = client.post(URL_VERIFY_OTP_AND_LOGIN, json=otp_data)
    logging.debug(f"Verify OTP response: {response.status_code}, {response.get_json()}")
    assert response.status_code == 200, f"OTP verification failed: {response.status_code}, {response.data}"

def test_verify_otp_and_login(client, init_database):
    logging.debug(f"Test user data: {test_userdata}")
    # Register user
    register_response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Register response: {register_response.status_code}, {register_response.data}")
    assert register_response.status_code == 201, f"Registration failed: {register_response.status_code}, {register_response.data}"

    # Confirm the account
    confirm_account(client, test_userdata['email'])

    # Initiate login with the newly registered user
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    assert response.status_code == 200, f"Login failed: {response.status_code}, {response.data}"

    # Retrieve the OTP sent
    account = Account.query.filter_by(email=test_userdata['email']).first()
    otp_record = OTP.query.filter_by(account_id=account.account_id).first()
    otp = otp_record.otp

    # Verify the OTP
    otp_data = {
        "email": test_userdata["email"],
        "otp": otp
    }
    response = client.post(URL_VERIFY_OTP_AND_LOGIN, json=otp_data)
    logging.debug(f"Verify OTP response: {response.status_code}, {response.get_json()}")
    assert response.status_code == 200, f"OTP verification failed: {response.status_code}, {response.data}"

    # Now the user should be able to login successfully
    final_login_response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Final Login response: {final_login_response.status_code}, {final_login_response.get_json()}")
    assert final_login_response.status_code == 200, f"Final login failed: {final_login_response.status_code}, {final_login_response.data}"
