"""
1Lap Dashboard Server - Flask WebSocket Application

This package contains the Flask application factory and core components.
"""

import os
from flask import Flask
from flask_socketio import SocketIO

__version__ = "0.1.0"

# Initialize SocketIO (will be bound to app in create_app)
socketio = SocketIO()


def create_app():
    """
    Flask application factory.

    Creates and configures the Flask application with SocketIO support,
    loads configuration, and registers routes.

    Returns:
        Flask: Configured Flask application instance
    """
    # Get the project root directory (parent of 'app' directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')

    # Create Flask app with correct template and static folders
    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    # Load configuration from config.py
    app.config.from_object('config.Config')

    # Initialize SocketIO with CORS support
    # cors_allowed_origins="*" allows connections from any origin (development)
    # In production, this should be restricted to specific domains
    socketio.init_app(app, cors_allowed_origins="*")

    # Import and register routes (must be after socketio.init_app)
    # This import is inside the function to avoid circular imports
    from app.main import register_routes
    register_routes(app)

    return app
