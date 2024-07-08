import logging
from flask.testing import FlaskClient
import pytest
from api.auth.utils import generate_token, verify_token

logging.basicConfig(level=logging.DEBUG)

URL_REGISTER_USER = "/auth/register"
URL_INITIATE_LOGIN = "/auth/initiate_login"
URL_VERIFY_OTP_AND_LOGIN = "/auth/verify_otp_and_login"
URL_CONFIRM_EMAIL = "/auth/confirm"

test_userdata = {
    "email": "testuser@example.com",
    "password": "Password123!",
    "username": "testuser",
    "date_of_birth": "2000-01-01",
    "address": "123 Test Street"
}

def confirm_account(client: FlaskClient, email: str):
    token = generate_token(email)
    logging.debug(f"Generated token: {token}")

    # Verifying the token right after generation to ensure it works
    email_from_token = verify_token(token)
    logging.debug(f"Email from token: {email_from_token}")

    assert email_from_token == email, "Generated token does not match email"

    confirm_url = f"{URL_CONFIRM_EMAIL}?token={token}"
    response = client.get(confirm_url)
    logging.debug(f"Confirm URL: {confirm_url}")
    logging.debug(f"Confirm response: {response.status_code}, {response.data}")
    assert response.status_code == 200, f"Failed to confirm account: {response.data}"

def test_register_user(client: FlaskClient):
    response = client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    assert response.status_code == 201

def test_initiate_login(client: FlaskClient, init_database):
    # Register user
    client.post(URL_REGISTER_USER, json=test_userdata)

    # Confirm the account
    confirm_account(client, test_userdata['email'])

    # Login with the newly registered user
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Error response: {response.get_json()}")
    assert response.status_code == 200

def test_verify_otp_and_login(client: FlaskClient, init_database):
    # Register user
    client.post(URL_REGISTER_USER, json=test_userdata)

    # Confirm the account
    confirm_account(client, test_userdata['email'])

    # Login with the newly registered user
    login_data = {
        "email": test_userdata["email"],
        "password": test_userdata["password"]
    }
    response = client.post(URL_INITIATE_LOGIN, json=login_data)
    logging.debug(f"Login data: {login_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Error response: {response.get_json()}")
    assert response.status_code == 200

    otp_response = response.get_json()
    if 'otp' not in otp_response:
        logging.error(f"OTP not found in response: {otp_response}")
        pytest.fail("OTP not found in response")

    otp = otp_response['otp']
    verify_otp_data = {
        "email": test_userdata["email"],
        "otp": otp
    }
    response = client.post(URL_VERIFY_OTP_AND_LOGIN, json=verify_otp_data)
    logging.debug(f"Verify OTP data: {verify_otp_data}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 200:
        logging.error(f"Error response: {response.get_json()}")
    assert response.status_code == 200
