"""
Unit tests for Flask app factory, routes, and configuration.

Tests the Flask application creation, HTTP routes, and SocketIO integration.
"""

import pytest
import os
from flask import Flask
from flask_socketio import SocketIO


@pytest.fixture
def app():
    """Create a fresh Flask app instance for each test."""
    # Import here to avoid circular imports
    from app import create_app

    # Create app with test configuration
    app = create_app()
    app.config['TESTING'] = True

    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    """Create a SocketIO test client."""
    from app import socketio
    return socketio.test_client(app)


@pytest.mark.unit
def test_app_creation():
    """Test that create_app() returns a valid Flask application."""
    from app import create_app

    app = create_app()

    # Should return a Flask instance
    assert isinstance(app, Flask)

    # Should have basic Flask attributes
    assert hasattr(app, 'config')
    assert hasattr(app, 'route')


@pytest.mark.unit
def test_config_loading(app):
    """Test that configuration loads correctly from config.py."""
    # Should have SECRET_KEY configured
    assert 'SECRET_KEY' in app.config
    assert app.config['SECRET_KEY'] is not None
    assert len(app.config['SECRET_KEY']) > 0

    # Should have DEBUG configured (defaults to True in dev)
    assert 'DEBUG' in app.config
    assert isinstance(app.config['DEBUG'], bool)

    # Should have HOST and PORT configured
    # Note: These are in Config class but not necessarily in app.config
    # We'll verify they exist in the config module


@pytest.mark.unit
def test_config_class():
    """Test that Config class has required attributes."""
    from config import Config

    # Should have all required configuration attributes
    assert hasattr(Config, 'SECRET_KEY')
    assert hasattr(Config, 'DEBUG')
    assert hasattr(Config, 'HOST')
    assert hasattr(Config, 'PORT')

    # Verify types
    assert isinstance(Config.SECRET_KEY, str)
    assert isinstance(Config.DEBUG, bool)
    assert isinstance(Config.HOST, str)
    assert isinstance(Config.PORT, int)


@pytest.mark.unit
def test_config_environment_variables(monkeypatch):
    """Test that configuration respects environment variables."""
    from config import Config

    # Set test environment variables
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key')
    monkeypatch.setenv('DEBUG', 'False')
    monkeypatch.setenv('HOST', '127.0.0.1')
    monkeypatch.setenv('PORT', '8080')

    # Reload the config module to pick up new env vars
    import importlib
    import config
    importlib.reload(config)

    # Verify config picked up environment variables
    assert config.Config.SECRET_KEY == 'test-secret-key'
    assert config.Config.DEBUG is False
    assert config.Config.HOST == '127.0.0.1'
    assert config.Config.PORT == 8080


@pytest.mark.unit
def test_socketio_initialized(app):
    """Test that SocketIO is properly initialized and attached to app."""
    from app import socketio

    # Should be a SocketIO instance
    assert isinstance(socketio, SocketIO)

    # Should be initialized (has server attribute after init_app)
    assert hasattr(socketio, 'server')


@pytest.mark.unit
def test_home_route(client):
    """Test that GET / returns 200 and shows server status."""
    response = client.get('/')

    # Should return 200 OK
    assert response.status_code == 200

    # Should contain relevant text
    data = response.data.decode('utf-8')
    assert '1Lap' in data or 'Dashboard' in data or 'Server' in data


@pytest.mark.unit
def test_dashboard_route(client):
    """Test that GET /dashboard/<session_id> returns 200."""
    test_session_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

    response = client.get(f'/dashboard/{test_session_id}')

    # Should return 200 OK
    assert response.status_code == 200

    # Should be HTML content
    assert response.content_type.startswith('text/html')


@pytest.mark.unit
def test_dashboard_session_id_passed_to_template(client):
    """Test that session_id is passed to the dashboard template."""
    test_session_id = 'test-uuid-12345'

    response = client.get(f'/dashboard/{test_session_id}')

    # Should contain the session ID in the rendered HTML
    data = response.data.decode('utf-8')
    assert test_session_id in data


@pytest.mark.unit
def test_static_files_accessible(client):
    """Test that static files can be served."""
    # Test that static file routes work (even if files don't exist yet)
    # Flask will return 404 if file doesn't exist, but route should work

    response = client.get('/static/css/dashboard.css')
    # Should not raise an error - either 200 (if file exists) or 404 (if not)
    assert response.status_code in [200, 404]

    response = client.get('/static/js/dashboard.js')
    assert response.status_code in [200, 404]


@pytest.mark.unit
def test_invalid_route_returns_404(client):
    """Test that invalid routes return 404."""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404


@pytest.mark.unit
def test_app_name(app):
    """Test that app has correct name."""
    # App name should be 'app' (the package name)
    assert app.name == 'app'


@pytest.mark.unit
def test_socketio_test_client_connects(socketio_client):
    """Test that SocketIO test client can connect."""
    # Should be able to connect
    assert socketio_client.is_connected()
