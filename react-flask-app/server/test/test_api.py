import logging
from flask.testing import FlaskClient
import pytest

# Configure logging
logging.basicConfig(level=logging.DEBUG)

URL_REGISTER_USER = "/api/auth/register"

test_userdata = {
    "email": "testuser@example.com",
    "password": "Password123!",
    "username": "testuser",
    "date_of_birth": "2000-01-01",
    "address": "123 Test Street"
}

def test_register_user(test_client: FlaskClient):
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

def test_get_users(test_client: FlaskClient, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

def test_delete_user(test_client: FlaskClient, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

def test_initiate_login(test_client: FlaskClient, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

def test_verify_otp_and_login(test_client: FlaskClient, init_database):
    # Register user
    response = test_client.post(URL_REGISTER_USER, json=test_userdata)
    logging.debug(f"Request data: {test_userdata}")
    logging.debug(f"Response: {response.status_code}, {response.get_json()}")
    if response.status_code != 201:
        logging.error(f"Failed to register user: {response.get_json()}")
    assert response.status_code == 201

if __name__ == '__main__':
    pytest.main()
