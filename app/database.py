# ==============================================================================
#  FILE: app/database.py
#  DESCRIPTION: Database connection with explicit initialization command.
# ==============================================================================
import sqlite3
import logging
import datetime
import click
from flask import g, current_app
from flask.cli import with_appcontext

# Import timezone utilities from the same package
from .utils import to_utc, DEFAULT_TZ

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def create_schema(db):
    """Creates the database tables from scratch."""
    cursor = db.cursor()
    cursor.executescript('''
        DROP TABLE IF EXISTS Users;
        DROP TABLE IF EXISTS Classes;
        DROP TABLE IF EXISTS Bookings;
        
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        );
        CREATE TABLE Classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            start_time TEXT NOT NULL,
            instructor VARCHAR(100) NOT NULL,
            capacity INTEGER NOT NULL,
            available_slots INTEGER NOT NULL
        );
        CREATE TABLE Bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (class_id) REFERENCES Classes(class_id)
        );
    ''')
    db.commit()

def seed_data(db):
    """Populates the database with sample data."""
    cursor = db.cursor()
    classes_data = [
        ('Yoga Flow', to_utc(datetime.datetime(2025, 7, 15, 8, 0), DEFAULT_TZ), 'Chloe', 20, 20),
        ('HIIT Blast', to_utc(datetime.datetime(2025, 7, 15, 18, 0), DEFAULT_TZ), 'Mike', 15, 15),
    ]
    cursor.executemany('INSERT INTO Classes (name, start_time, instructor, capacity, available_slots) VALUES (?, ?, ?, ?, ?);', classes_data)
    
    users_data = [
        ('Alice', 'alice@example.com', 'dummy_hash_1'), 
        ('Bob', 'bob@example.com', 'dummy_hash_2')
    ]
    cursor.executemany('INSERT INTO Users (name, email, password_hash) VALUES (?, ?, ?);', users_data)
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db = get_db()
    create_schema(db)
    seed_data(db)
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    # This ensures close_db is called when the app context is torn down.
    app.teardown_appcontext(close_db)
    # Add the new command to the app, so it can be called from the command line.
    app.cli.add_command(init_db_command)
