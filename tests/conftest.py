"""
Pytest configuration and shared fixtures for dashboard server tests.

This module provides reusable test fixtures for:
- Flask application instances (for HTTP route testing)
- SocketIO clients (for WebSocket testing)
- SessionManager instances (for session management testing)
- Sample data (telemetry, setup, etc.)

Usage:
    # In your test file:
    def test_something(app, client, session_manager):
        # Use fixtures directly as function parameters
        assert client.get('/').status_code == 200

Organization:
    - Application Fixtures: Flask app, test client, SocketIO client
    - Component Fixtures: SessionManager, other components
    - Data Fixtures: Sample telemetry, setup, etc.

Notes:
    - Some fixtures are skeletons/placeholders for features not yet implemented
    - These will be activated when Flask app and WebSocket server are complete
    - All fixtures use function scope (fresh instance per test) unless noted
"""

import pytest
from datetime import datetime, timezone


# ==============================================================================
# APPLICATION FIXTURES (Flask, SocketIO)
# ==============================================================================
# NOTE: These fixtures are currently skeletons/placeholders.
# They will be activated once the Flask app and WebSocket server are implemented.
# ==============================================================================

@pytest.fixture
def app():
    """
    Create and configure Flask application instance for testing.

    Returns:
        Flask: Application instance with TESTING=True

    Status: ACTIVE - Flask app is implemented
    Usage:
        def test_route(app):
            with app.app_context():
                # Test something
                pass
    """
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """
    Create Flask test client for making HTTP requests.

    Args:
        app: Flask application fixture

    Returns:
        FlaskClient: Test client for HTTP requests

    Status: ACTIVE - Flask app is implemented
    Usage:
        def test_homepage(client):
            response = client.get('/')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    """
    Create SocketIO test client for WebSocket communication testing.

    Args:
        app: Flask application fixture

    Returns:
        SocketIOTestClient: Test client for WebSocket events

    Status: ACTIVE - Flask-SocketIO is implemented
    Usage:
        def test_websocket_connect(socketio_client):
            assert socketio_client.is_connected()
            socketio_client.emit('test_event', {'data': 'test'})
            received = socketio_client.get_received()
    """
    from app import socketio
    return socketio.test_client(app)


# ==============================================================================
# COMPONENT FIXTURES (SessionManager, etc.)
# ==============================================================================

@pytest.fixture
def session_manager():
    """
    Create a fresh SessionManager instance for testing.

    Returns:
        SessionManager: New instance with empty sessions dict

    Status: ACTIVE - SessionManager is implemented
    Usage:
        def test_create_session(session_manager):
            session_id = session_manager.create_session()
            assert isinstance(session_id, str)

    Notes:
        - Each test gets a fresh instance (function scope)
        - No shared state between tests
        - Safe for parallel test execution
    """
    from app.session_manager import SessionManager
    return SessionManager()


# ==============================================================================
# DATA FIXTURES (Sample telemetry, setup, etc.)
# ==============================================================================

@pytest.fixture
def sample_setup_data():
    """
    Sample car setup data from LMU REST API.

    Returns:
        dict: Car setup with suspension, aero, brakes

    Structure:
        {
            'suspension': {...},
            'aerodynamics': {...},
            'brakes': {...}
        }

    Usage:
        def test_setup_storage(session_manager, sample_setup_data):
            session_id = session_manager.create_session()
            session_manager.update_setup(session_id, sample_setup_data, timestamp)
    """
    return {
        "suspension": {
            "front_spring_rate": 120.5,
            "rear_spring_rate": 115.3,
            "front_damper": 8,
            "rear_damper": 7
        },
        "aerodynamics": {
            "front_wing": 5,
            "rear_wing": 8
        },
        "brakes": {
            "brake_bias": 56.5
        }
    }


@pytest.fixture
def sample_telemetry_data():
    """
    Sample telemetry data from monitor (shared memory).

    Returns:
        dict: Real-time telemetry with fuel, tires, temps, etc.

    Structure:
        {
            'timestamp': ISO timestamp,
            'lap': int,
            'position': int,
            'fuel': float,
            'tire_pressures': {...},
            'tire_temps': {...},
            ...
        }

    Usage:
        def test_telemetry_update(session_manager, sample_telemetry_data):
            session_id = session_manager.create_session()
            session_manager.update_telemetry(session_id, sample_telemetry_data)

    Notes:
        - Timestamp is dynamically generated per test
        - Values are realistic racing data
        - Matches expected structure from monitor
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lap": 5,
        "position": 2,
        "fuel": 45.3,
        "fuel_capacity": 80.0,
        "tire_pressures": {
            "fl": 28.5,
            "fr": 28.7,
            "rl": 27.8,
            "rr": 28.0
        },
        "tire_temps": {
            "fl": 85.2,
            "fr": 86.1,
            "rl": 84.5,
            "rr": 85.0
        },
        "brake_temps": {
            "fl": 450.0,
            "fr": 455.0,
            "rl": 420.0,
            "rr": 425.0
        },
        "engine_water_temp": 92.5,
        "track_temp": 28.5,
        "ambient_temp": 22.0,
        "player_name": "Test Driver",
        "car_name": "Test Car",
        "track_name": "Test Track",
        "session_type": "race"
    }
