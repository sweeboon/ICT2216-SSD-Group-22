import pytest
from api import create_app, db as _db
from api.models import Account
from datetime import datetime

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    """A new database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def init_database(db, app):
    """Initialize the database with a user for testing."""
    with app.app_context():
        user = Account(
            email="testuser@example.com",
            password="Password123!",
            name="testuser",
            date_of_birth=datetime.strptime("2000-01-01", "%Y-%m-%d").date(),
            address="123 Test Street"
        )
        db.session.add(user)
        db.session.commit()
    yield db
