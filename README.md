# booking_api_omnify

Fitness Studio Booking API
A simple and robust booking API for a fictional fitness studio, built with Python and Flask. This API allows clients to view upcoming classes, book a spot, and view their existing bookings.

Features

View Classes: Get a list of all upcoming classes.

Book a Spot: Book a spot in an available class.

View Bookings: Retrieve all bookings for a specific user.

Timezone Aware: All class times are stored in UTC and can be displayed in any user-specified timezone.

Error Handling: Graceful handling of common errors like missing fields or booking a full class.

Unit Tested: Comes with a full suite of unit tests using pytest to ensure reliability.

Setup and Installation
Follow these steps to get the application running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

1. Clone the Repository
First, get the project files onto your machine. If you have git installed:

git clone <repository-url>
cd <project-directory>

If not, simply download and unzip the project files into a new directory.

2. Create a Virtual Environment
It's highly recommended to use a virtual environment to keep project dependencies isolated.

### Create a virtual environment
python -m venv venv

### Activate the virtual environment
### On Windows:
venv\Scripts\activate
### On macOS/Linux:
source venv/bin/activate

3. Install Dependencies
Install all the required Python packages from requirements.txt.

pip install Flask pytz pytest

(Note: If you were given a requirements.txt file, you would run pip install -r requirements.txt)

4. Initialize the Database
The application uses a CLI command to create the database file and populate it with initial data.

### Make sure your FLASK_APP environment variable is set
### On Windows (Command Prompt):
set FLASK_APP=run.py
### On Windows (PowerShell):
$env:FLASK_APP="run.py"
### On macOS/Linux:
export FLASK_APP=run.py

## Run the init-db command
flask init-db

You should see a message: Initialized the database. This will create an instance/fitness_studio.sqlite file in your project directory.

Running the Application
Development Server
To start the local development server:

flask run --port=5001

The API will now be running at http://127.0.0.1:5001.

Running Unit Tests
To verify that everything is working correctly, you can run the built-in test suite.

pytest -v

All tests should pass, confirming that the application logic is sound.

API Endpoints Guide
Here is how to interact with the API using cURL.

1. Get Available Classes
Returns a list of all upcoming fitness classes.

Endpoint: GET /api/classes

Method: GET

Query Parameters:

timezone (optional): A valid timezone string (e.g., America/New_York, Europe/London). Defaults to UTC.

Sample Request (Default UTC):

curl http://127.0.0.1:5001/api/classes

Sample Request (IST Timezone):

curl "http://127.0.0.1:5001/api/classes?timezone=Asia/Kolkata"

Success Response (200 OK):

[
  {
    "available_slots": 20,
    "class_id": 1,
    "instructor": "Chloe",
    "name": "Yoga Flow",
    "start_time": "2025-07-15 08:00:00 IST+0530"
  },
  {
    "available_slots": 15,
    "class_id": 2,
    "instructor": "Mike",
    "name": "HIIT Blast",
    "start_time": "2025-07-15 18:00:00 IST+0530"
  }
]

2. Book a Class
Creates a booking for a user in a specific class.

Endpoint: POST /api/book

Method: POST

Body (JSON):

class_id (integer, required)

client_name (string, required)

client_email (string, required)

Sample Request:

curl -X POST -H "Content-Type: application/json" \
     -d '{"class_id": 1, "client_name": "John Doe", "client_email": "john.doe@example.com"}' \
     http://127.0.0.1:5001/api/book

Success Response (201 Created):

{
  "success": true,
  "message": "Booking confirmed!",
  "booking_id": 1
}

Error Response (400 Bad Request - No Slots):

{
  "error": "No available slots for this class."
}

3. View Your Bookings
Returns a list of all bookings made by a specific user, identified by their email.

Endpoint: GET /api/bookings

Method: GET

Query Parameters:

email (string, required): The email of the user whose bookings you want to retrieve.

timezone (optional): A valid timezone string. Defaults to UTC.

Sample Request:

curl "http://127.0.0.1:5001/api/bookings?email=john.doe@example.com&timezone=Asia/Kolkata"

Success Response (200 OK):

[
  {
    "booking_date": "2025-07-05 12:30:00 IST+0530",
    "instructor": "Chloe",
    "name": "Yoga Flow",
    "start_time": "2025-07-15 08:00:00 IST+0530"
  }
]

Error Response (404 Not Found):

{
  "message": "No bookings found for this email."
}
