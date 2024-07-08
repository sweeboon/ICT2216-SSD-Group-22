import logging
from flask.testing import FlaskClient
import pytest

# Configure logging
logging.basicConfig(level=logging.DEBUG)

URL_REGISTER_USER = "/api/auth/register"
URL_INITIATE_LOGIN = "/api/auth/initiate_login"
URL_VERIFY_OTP_AND_LOGIN = "/api/auth/verify_otp_and_login"

test_userdata = {
    "email": "testuser@example.com",
    "password": "Password123!",
    "username": "testuser",
    "date_of_birth": "2000-01-01",
    "address": "123 Test Street"
}

def test_register_user(client: FlaskClient):
    response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

def test_initiate_login(client: FlaskClient, init_database):
    # Register user
    response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

    # Initiate login
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Failed to initiate login: {response.get_json()}")
    assert response.status_code == 200

def test_verify_otp_and_login(client: FlaskClient, init_database):
    # Register user
    response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

    # Initiate login
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Failed to initiate login: {response.get_json()}")
    assert response.status_code == 200

    otp = response.get_json().get('otp')  # Assuming the OTP is returned in the response for testing
    verify_otp_data = {
        "email": test_userdata["email"],
        "otp": otp
    }
    response = client.post(URL_VERIFY_OTP_AND_LOGIN, json=verify_otp_data)
    logging.debug(f"Verify OTP data: {verify_otp_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Failed to verify OTP and login: {response.get_json()}")
    assert response.status_code == 200
