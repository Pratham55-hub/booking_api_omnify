# ==============================================================================
#  FILE: config.py
#  DESCRIPTION: Simplified application configuration.
# ==============================================================================
import os

# Get the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration."""
    SECRET_KEY = 'a-simple-secret-key'
    DATABASE = os.path.join(basedir, 'instance', 'fitness_studio.sqlite')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Use a separate in-memory DB for tests to keep them isolated and fast.
    DATABASE = ':memory:'