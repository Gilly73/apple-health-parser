"""
Pytest configuration and fixtures.
Shared test utilities used across all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# Test database configuration
# Uses SQLite in-memory database for speed
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_engine():
    """Create test database engine (in-memory SQLite)"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_client(test_session):
    """Create FastAPI test client with test database"""
    def override_get_db():
        try:
            yield test_session
        finally:
            test_session.close()

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "google_id": "123456789",
        "email": "test@example.com",
        "name": "Test User",
        "profile_picture_url": "https://example.com/pic.jpg"
    }


@pytest.fixture
def sample_workout_data():
    """Sample workout data for tests"""
    return {
        "date": "2024-01-15",
        "time": "10:30:00",
        "type": "Running",
        "duration_min": 30,
        "calories": 250,
        "source": "Apple Watch"
    }