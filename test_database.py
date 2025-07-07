# ==============================================================================
#  FILE: test_database.py
#  DESCRIPTION: Unit tests for database functions.
# ==============================================================================
import pytest
import sqlite3
from app.database import get_db

# The 'app' fixture is now defined in conftest.py and available automatically.

def test_get_close_db(app):
    """
    Tests that get_db returns the same connection within an app context
    and that the connection is closed afterwards.
    """
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    assert 'closed' in str(e.value)

def test_init_db_command(app, monkeypatch, tmp_path):
    """
    Tests the 'init-db' Flask CLI command using a temporary file database
    to ensure the side-effects of the command can be verified.
    """
    # Create a path for a temporary database file.
    db_path = tmp_path / "test.db"
    
    # Use monkeypatch to temporarily change the app's DATABASE config to
    # point to our temporary file. This happens only for this test.
    monkeypatch.setitem(app.config, 'DATABASE', db_path)

    # Run the init-db command. It will now write to the file at db_path.
    runner = app.test_cli_runner()
    result = runner.invoke(args=['init-db'])
    assert 'Initialized the database.' in result.output

    # The command has finished. To verify its work, we connect directly
    # to the temporary database file it created.
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Classes'")
    
    # This assertion will now pass because the table exists in the file.
    assert cursor.fetchone() is not None, "The 'Classes' table was not created by init-db command."
