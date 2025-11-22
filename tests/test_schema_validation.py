import pytest


def _setup_session_and_clients(app):
    from app import socketio
    monitor = socketio.test_client(app)
    monitor.emit('request_session_id', {})
    session_id = monitor.get_received()[0]['args'][0]['session_id']

    dashboard = socketio.test_client(app)
    dashboard.emit('join_session', {'session_id': session_id})
    dashboard.get_received()  # clear any initial messages
    return monitor, dashboard, session_id


def test_invalid_setup_rejected(app):
    from app.main import VALIDATION_ENABLED
    if not VALIDATION_ENABLED:
        pytest.skip("Schema validation not enabled")

    monitor, dashboard, session_id = _setup_session_and_clients(app)

    # Missing required 'timestamp'
    monitor.emit('setup_data', {
        'session_id': session_id,
        'setup': {'suspension': {'front_spring_rate': 120.0}}
    })

    received = dashboard.get_received()
    assert all(msg['name'] != 'setup_update' for msg in received)


def test_invalid_telemetry_rejected(app):
    from app.main import VALIDATION_ENABLED
    if not VALIDATION_ENABLED:
        pytest.skip("Schema validation not enabled")

    monitor, dashboard, session_id = _setup_session_and_clients(app)

    # Telemetry payload missing required 'lap' and other fields
    monitor.emit('telemetry_update', {
        'session_id': session_id,
        'telemetry': {
            'timestamp': '2024-01-01T00:00:00Z'
        }
    })

    received = dashboard.get_received()
    assert all(msg['name'] != 'telemetry_update' for msg in received)

