"""
Configuration management for 1Lap Dashboard Server.

Loads configuration from environment variables with sensible defaults.
Supports both development and production environments.
"""

import os


class Config:
    """
    Flask application configuration.

    Configuration values are loaded from environment variables with defaults.
    Use environment variables to override defaults in production.
    """

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Debug mode (True for development, False for production)
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Server host (0.0.0.0 allows external connections)
    HOST = os.environ.get('HOST', '0.0.0.0')

    # Server port
    PORT = int(os.environ.get('PORT', 5000))

    # CORS configuration for WebSocket connections
    # In production, you should restrict this to specific origins
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
