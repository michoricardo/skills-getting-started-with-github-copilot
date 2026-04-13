"""
Pytest configuration and shared fixtures for API tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for API testing.
    Uses dependency override to reset app state between tests.
    """
    # Import fresh app for each test
    from app import app, activities
    
    # Create test client
    test_client = TestClient(app)
    
    # Save original state
    original_state = {
        activity_name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for activity_name, activity in activities.items()
    }
    
    yield test_client
    
    # Restore original state after test
    for activity_name, activity in activities.items():
        activity["participants"] = original_state[activity_name]["participants"].copy()
