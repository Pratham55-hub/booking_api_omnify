# ==============================================================================
#  FILE: run.py
#  DESCRIPTION: Main entry point for running the application.
# ==============================================================================

# Import the application factory from the 'app' package
from app import create_app

# Create an instance of the app using the factory
# You can pass a different config class for production, e.g., 'config.ProductionConfig'
app = create_app('config.DevelopmentConfig')

if __name__ == '__main__':
    # The app.run() method is suitable for development.
    # For production, use a WSGI server like Gunicorn or uWSGI.
    # Example: gunicorn -w 4 "run:app"
    app.run(port=5001)
