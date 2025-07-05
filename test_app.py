# ==============================================================================
#  FILE: test_app.py
#  DESCRIPTION: Unit tests for the Fitness Studio API.
# ==============================================================================
import pytest
import json
from app import create_app
from app.database import create_schema, seed_data, get_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Use the TestingConfig to ensure tests run on a separate, in-memory DB
    app = create_app('config.TestingConfig')
    yield app

@pytest.fixture
def client(app):
    """A test client for the app that correctly handles the app context."""
    # The with app.app_context() block is crucial. It ensures that the
    # database connection (g.db) is available for the duration of the setup
    # AND the test itself.
    with app.app_context():
        # Set up the database within the application context
        create_schema(get_db())
        seed_data(get_db())
        # Yield the test client while the context is still active.
        # The test will run at this point.
        yield app.test_client()
    # After the test is complete, the context will be popped, and the
    # in-memory database will be torn down automatically.

# --- Test Cases for /api/classes ---

def test_get_classes_success(client):
    """Test successfully fetching available classes."""
    response = client.get('/api/classes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0  # Assuming seed data has classes
    assert 'class_id' in data[0]
    assert 'start_time' in data[0]

def test_get_classes_with_timezone(client):
    """Test fetching classes with a specific timezone."""
    response = client.get('/api/classes?timezone=America/New_York')
    assert response.status_code == 200
    data = response.get_json()
    # Check if the timezone information is correctly appended
    assert 'EDT' in data[0]['start_time'] or 'EST' in data[0]['start_time']

def test_get_classes_invalid_timezone(client):
    """Test fetching classes with an invalid timezone string."""
    response = client.get('/api/classes?timezone=Invalid/Timezone')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid timezone' in data['error']

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
    assert 'booking_id' in data

def test_book_class_missing_fields(client):
    """Test booking with missing required fields."""
    booking_data = {
        "class_id": 1,
        "client_name": "Test User"
        # client_email is missing
    }
    response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'Missing data' in data['error']

def test_book_nonexistent_class(client):
    """Test booking a class that does not exist."""
    booking_data = {
        "class_id": 999,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Class not found.'

def test_book_full_class(client):
    """Test overbooking by booking a class until it's full and then one more time."""
    # The HIIT class has a capacity of 15. Let's book it 15 times.
    for i in range(15):
        response = client.post('/api/book', data=json.dumps({
            "class_id": 2,
            "client_name": f"User {i}",
            "client_email": f"user{i}@example.com"
        }), content_type='application/json')
        assert response.status_code == 201 # Verify each booking succeeds

    # Now, try to book it one more time
    final_booking_response = client.post('/api/book', data=json.dumps({
        "class_id": 2,
        "client_name": "Extra User",
        "client_email": "extra@example.com"
    }), content_type='application/json')
    
    assert final_booking_response.status_code == 400
    data = final_booking_response.get_json()
    assert data['error'] == 'No available slots for this class.'

def test_book_same_class_twice(client):
    """Test that a user cannot book the same class more than once."""
    booking_data = {
        "class_id": 1,
        "client_name": "Eager User",
        "client_email": "eager@example.com"
    }
    # First booking should succeed
    first_response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert first_response.status_code == 201
    
    # Second booking should fail
    second_response = client.post('/api/book', data=json.dumps(booking_data), content_type='application/json')
    assert second_response.status_code == 400
    data = second_response.get_json()
    assert data['error'] == 'You are already booked for this class.'

# --- Test Cases for /api/bookings ---

def test_get_bookings_success(client):
    """Test getting bookings for a user who has made a booking."""
    # First, make a booking
    client.post('/api/book', data=json.dumps({
        "class_id": 1,
        "client_name": "Booking Checker",
        "client_email": "checker@example.com"
    }), content_type='application/json')

    # Then, retrieve the bookings for that user
    response = client.get('/api/bookings?email=checker@example.com')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Yoga Flow'

def test_get_bookings_no_email(client):
    """Test that the /bookings endpoint requires an email parameter."""
    response = client.get('/api/bookings')
    assert response.status_code == 400
    data = response.get_json()
    assert 'Email query parameter is required' in data['error']

def test_get_bookings_for_user_with_no_bookings(client):
    """Test getting bookings for a valid email that has no bookings."""
    response = client.get('/api/bookings?email=nobookings@example.com')
    assert response.status_code == 404
    data = response.get_json()
    assert 'No bookings found' in data['message']
