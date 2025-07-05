# ==============================================================================
#  FILE: app/__init__.py
#  DESCRIPTION: Simplified application factory.
# ==============================================================================
import logging
import os
from flask import Flask, jsonify

def create_app(config_class='config.DevelopmentConfig'):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Directory already exists

    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize database
    from . import database
    database.init_app(app)

    # Register blueprints
    from . import routes
    app.register_blueprint(routes.bp, url_prefix='/api')

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': 'The requested URL was not found on the server.'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal Server Error: {error}")
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.route('/')
    def index():
        return "Welcome to the Fitness Studio API! Visit /api/classes to see available classes."

    return app
