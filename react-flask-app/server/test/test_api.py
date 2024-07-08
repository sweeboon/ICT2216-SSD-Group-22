import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, Account
from main import app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration for testing with an in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    yield db  # Provide the session to the tests
    db.close()
    Base.metadata.drop_all(bind=engine)  # Drop tables after tests

@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# Sample user data for testing
test_userdata = {
    "email": "testuser@gmail.com",
    "password": "Testing123@!",
    "name": "testname",
    "date_of_birth": "2000-01-01",
    "address": "123 Test St, Test City, Test Country"
}

# URLs for API endpoints
URL_GET_USER_BY_EMAIL = "/api/user/email/{email}".format(email=test_userdata["email"])
URL_CREATE_USER = "/api/user"
URL_DELETE_USER = "/api/delete_user"

def test_create_user(client: TestClient):
    # Check if the user already exists
    response = client.get(URL_GET_USER_BY_EMAIL)
    assert response.status_code == 404  # Assuming the user does not exist

    # Create user
    response = client.post(URL_CREATE_USER, json=test_userdata)
    assert response.status_code == 201  # Successful creation returns 201

    # Verify the user is created
    response = client.get(URL_GET_USER_BY_EMAIL)
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == test_userdata['email']

    # Delete user
    json_data = {"email": test_userdata["email"]}
    response = client.post(URL_DELETE_USER, json=json_data)
    assert response.status_code == 200  # Successful deletion returns 200
    data = response.json()
    assert data['message'] == f"{test_userdata['email']} account deleted."

def test_get_user_by_id(client: TestClient):
    # Create user
    response = client.post(URL_CREATE_USER, json=test_userdata)
    assert response.status_code == 201

    # Get user_id using email
    response = client.get(URL_GET_USER_BY_EMAIL)
    assert response.status_code == 200
    data = response.json()
    user_id = data['user_id']

    # Get user using user_id
    URL_GET_USER_BY_ID = f"/api/user/{user_id}"
    response = client.get(URL_GET_USER_BY_ID)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id

    # Delete user
    json_data = {"email": test_userdata["email"]}
    response = client.post(URL_DELETE_USER, json=json_data)
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == f"{test_userdata['email']} account deleted."
