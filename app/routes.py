# ==============================================================================
#  FILE: app/routes.py
#  DESCRIPTION: API endpoints with timezone and validation handling.
# ==============================================================================
import sqlite3
import datetime
import logging
import re
import pytz
from flask import request, jsonify, Blueprint

from .database import get_db
from .utils import from_utc, UTC

bp = Blueprint('api', __name__)

@bp.route('/classes', methods=['GET'])
def get_classes():
    try:
        user_tz_str = request.args.get('timezone', 'UTC')
        user_tz = pytz.timezone(user_tz_str)
    except pytz.UnknownTimeZoneError:
        return jsonify({'error': 'Invalid timezone specified.'}), 400

    db = get_db()
    cursor = db.cursor()
    
    now_utc = datetime.datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT class_id, name, start_time, instructor, available_slots FROM Classes WHERE start_time > ? ORDER BY start_time ASC", (now_utc,))
    classes_utc = cursor.fetchall()

    # Convert UTC times from DB to user's specified timezone for display
    classes_list = [
        {
            "class_id": row["class_id"],
            "name": row["name"],
            "start_time": from_utc(row["start_time"], user_tz),
            "instructor": row["instructor"],
            "available_slots": row["available_slots"]
        } for row in classes_utc
    ]
    
    return jsonify(classes_list)

@bp.route('/book', methods=['POST'])
def book_class():
    data = request.get_json()
    # Check for missing fields
    required = ['class_id', 'client_name', 'client_email']
    if not data or not all(k in data for k in required):
        return jsonify({'error': f'Missing data: {", ".join(required)} are required.'}), 400

    # Add basic input validation
    if not isinstance(data['class_id'], int):
        return jsonify({'error': 'Invalid class_id: must be an integer.'}), 400
    
    client_email = data['client_email'].lower() # Normalize email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", client_email):
        return jsonify({'error': 'Invalid email format.'}), 400

    class_id = data['class_id']
    client_name = data['client_name']

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('BEGIN')

        cursor.execute("SELECT user_id FROM Users WHERE email = ?", (client_email,))
        user = cursor.fetchone()
        if user:
            user_id = user['user_id']
        else:
            cursor.execute("INSERT INTO Users (name, email, password_hash) VALUES (?, ?, ?)",
                           (client_name, client_email, 'dummy_password'))
            user_id = cursor.lastrowid

        # Check class availability and that it hasn't started
        now_utc = datetime.datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT available_slots, start_time FROM Classes WHERE class_id = ?", (class_id,))
        class_info = cursor.fetchone()

        if not class_info:
            raise ValueError("Class not found.")
        if class_info['start_time'] <= now_utc:
            raise ValueError("Cannot book a class that has already started.")
        if class_info['available_slots'] <= 0:
            raise ValueError("No available slots for this class.")
        
        # Check if user is already booked for this class
        cursor.execute("SELECT booking_id FROM Bookings WHERE user_id = ? AND class_id = ?", (user_id, class_id))
        if cursor.fetchone():
            raise ValueError("You are already booked for this class.")

        cursor.execute("UPDATE Classes SET available_slots = available_slots - 1 WHERE class_id = ?", (class_id,))
        cursor.execute("INSERT INTO Bookings (user_id, class_id) VALUES (?, ?)", (user_id, class_id))
        booking_id = cursor.lastrowid
        
        db.commit()
        
        logging.info(f"Booking successful for {client_email} for class_id {class_id}. ID: {booking_id}")
        return jsonify({'success': True, 'message': 'Booking confirmed!', 'booking_id': booking_id}), 201

    except (sqlite3.Error, ValueError) as e:
        db.rollback()
        logging.error(f"Error during booking: {e}")
        return jsonify({'error': str(e)}), 400

@bp.route('/bookings', methods=['GET'])
def get_bookings():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email query parameter is required.'}), 400

    try:
        user_tz_str = request.args.get('timezone', 'UTC')
        user_tz = pytz.timezone(user_tz_str)
    except pytz.UnknownTimeZoneError:
        return jsonify({'error': 'Invalid timezone specified.'}), 400

    db = get_db()
    cursor = db.cursor()
    query = """
        SELECT c.name, c.instructor, c.start_time, b.booking_date
        FROM Bookings b
        JOIN Users u ON b.user_id = u.user_id
        JOIN Classes c ON b.class_id = c.class_id
        WHERE u.email = ? ORDER BY c.start_time ASC;
    """
    cursor.execute(query, (email.lower(),)) # Use normalized email
    bookings_utc = cursor.fetchall()
    
    if not bookings_utc:
        return jsonify({'message': 'No bookings found for this email.'}), 404

    # Convert UTC times to user's timezone for display
    bookings_list = [
        {
            "name": row["name"],
            "instructor": row["instructor"],
            "start_time": from_utc(row["start_time"], user_tz),
            "booking_date": from_utc(row["booking_date"], user_tz)
        } for row in bookings_utc
    ]
    return jsonify(bookings_list)
