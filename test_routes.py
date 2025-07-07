# ==============================================================================
#  FILE: test_routes.py
#  DESCRIPTION: Unit tests for the API endpoints.
# ==============================================================================
import pytest
import json
from app.database import create_schema, seed_data, get_db

# The 'app' fixture is now defined in conftest.py and available automatically.

@pytest.fixture
def client(app):
    """
    A test client for the app. This fixture depends on the 'app' fixture
    from conftest.py and sets up a clean database for each test.
    """
    with app.app_context():
        create_schema(get_db())
        seed_data(get_db())
        yield app.test_client()

# --- Test Cases for /api/classes ---

def test_get_classes_success(client):
    """Test successfully fetching available classes."""
    response = client.get('/api/classes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'class_id' in data[0]

def test_get_classes_with_timezone(client):
    """Test fetching classes with a specific timezone."""
    response = client.get('/api/classes?timezone=America/New_York')
    assert response.status_code == 200
    data = response.get_json()
    assert 'EDT' in data[0]['start_time'] or 'EST' in data[0]['start_time']

# --- Test Cases for /api/book ---

def test_book_class_success(client):
    """Test a successful class booking."""
    booking_data = {
        "class_id": 1,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True

def test_book_nonexistent_class(client):
    """Test booking a class that does not exist."""
    booking_data = {
        "class_id": 999,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Class not found.'

def test_book_full_class(client):
    """Test overbooking by booking a class until it's full and then one more time."""
    for i in range(15):
        client.post('/api/book', data=json.dumps({
            "class_id": 2, "client_name": f"User {i}", "client_email": f"user{i}@example.com"
        }), content_type='application/json')

    final_response = client.post('/api/book', data=json.dumps({
        "class_id": 2, "client_name": "Extra User", "client_email": "extra@example.com"
    }), content_type='application/json')
    
    assert final_response.status_code == 400
    assert final_response.get_json()['error'] == 'No available slots for this class.'

# --- Test Cases for /api/bookings ---

def test_get_bookings_success(client):
    """Test getting bookings for a user who has made a booking."""
    client.post('/api/book', data=json.dumps({
        "class_id": 1, "client_name": "Booking Checker", "client_email": "checker@example.com"
    }), content_type='application/json')

    response = client.get('/api/bookings?email=checker@example.com')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Yoga Flow'

def test_get_bookings_no_email(client):
    """Test that the /bookings endpoint requires an email parameter."""
    response = client.get('/api/bookings')
    assert response.status_code == 400
    assert 'Email query parameter is required' in response.get_json()['error']
