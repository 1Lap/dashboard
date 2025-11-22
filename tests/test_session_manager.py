"""
Unit tests for SessionManager class.

Tests session creation, data storage, and retrieval.
"""

import pytest
import uuid
from datetime import datetime
from app.session_manager import SessionManager


@pytest.fixture
def session_manager():
    """Create a fresh SessionManager instance for each test."""
    return SessionManager()


@pytest.mark.unit
def test_create_session(session_manager):
    """Test that create_session generates a valid UUID."""
    session_id = session_manager.create_session()

    # Should return a string
    assert isinstance(session_id, str)

    # Should be a valid UUID format (36 chars with hyphens)
    assert len(session_id) == 36
    assert session_id.count('-') == 4

    # Session should exist in storage
    assert session_id in session_manager.get_active_sessions()


@pytest.mark.unit
def test_create_multiple_sessions(session_manager):
    """Test that multiple sessions have unique IDs."""
    session_ids = [session_manager.create_session() for _ in range(10)]

    # All IDs should be unique
    assert len(session_ids) == len(set(session_ids))

    # All sessions should be active
    active = session_manager.get_active_sessions()
    assert len(active) == 10


@pytest.mark.unit
def test_update_setup(session_manager, sample_setup_data):
    """Test storing setup data for a session."""
    session_id = session_manager.create_session()
    timestamp = datetime.utcnow().isoformat()

    # Update setup data
    session_manager.update_setup(session_id, sample_setup_data, timestamp)

    # Retrieve and verify
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session['setup'] == sample_setup_data
    assert session['setup_timestamp'] == timestamp


@pytest.mark.unit
def test_update_telemetry(session_manager, sample_telemetry_data):
    """Test storing telemetry data for a session."""
    session_id = session_manager.create_session()

    # Update telemetry
    session_manager.update_telemetry(session_id, sample_telemetry_data)

    # Retrieve and verify
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session['telemetry'] == sample_telemetry_data
    assert 'last_update' in session

    # Verify timestamp format (ISO 8601)
    datetime.fromisoformat(session['last_update'])  # Should not raise


@pytest.mark.unit
def test_get_session(session_manager, sample_setup_data, sample_telemetry_data):
    """Test retrieving complete session data."""
    session_id = session_manager.create_session()
    timestamp = datetime.utcnow().isoformat()

    # Add both setup and telemetry
    session_manager.update_setup(session_id, sample_setup_data, timestamp)
    session_manager.update_telemetry(session_id, sample_telemetry_data)

    # Retrieve session
    session = session_manager.get_session(session_id)

    # Verify structure
    assert session['session_id'] == session_id
    assert 'created_at' in session
    assert session['setup'] == sample_setup_data
    assert session['setup_timestamp'] == timestamp
    assert session['telemetry'] == sample_telemetry_data
    assert 'last_update' in session


@pytest.mark.unit
def test_get_nonexistent_session(session_manager):
    """Test that getting a non-existent session returns None."""
    result = session_manager.get_session("nonexistent-uuid")
    assert result is None


@pytest.mark.unit
def test_delete_session(session_manager):
    """Test session deletion."""
    session_id = session_manager.create_session()

    # Verify session exists
    assert session_id in session_manager.get_active_sessions()

    # Delete session
    session_manager.delete_session(session_id)

    # Verify session is gone
    assert session_id not in session_manager.get_active_sessions()
    assert session_manager.get_session(session_id) is None


@pytest.mark.unit
def test_get_active_sessions(session_manager):
    """Test listing all active session IDs."""
    # Start with empty list
    assert session_manager.get_active_sessions() == []

    # Create multiple sessions
    ids = [session_manager.create_session() for _ in range(5)]

    # Should return all session IDs
    active = session_manager.get_active_sessions()
    assert len(active) == 5
    assert set(active) == set(ids)

    # Delete one session
    session_manager.delete_session(ids[0])
    active = session_manager.get_active_sessions()
    assert len(active) == 4
    assert ids[0] not in active


# ============================================================================
# URL Generation and Validation Tests
# ============================================================================

@pytest.mark.unit
def test_session_id_is_valid_uuid4(session_manager):
    """Test that session IDs are valid UUID4 format."""
    session_id = session_manager.create_session()

    # Should be parseable as UUID
    parsed_uuid = uuid.UUID(session_id)

    # Should be UUID version 4 (random)
    assert parsed_uuid.version == 4

    # Should match original string
    assert str(parsed_uuid) == session_id


@pytest.mark.unit
def test_session_id_uniqueness_large_sample(session_manager):
    """Test that session IDs are unique across large sample (collision test)."""
    # Generate 1000 session IDs
    session_ids = [session_manager.create_session() for _ in range(1000)]

    # All should be unique
    assert len(session_ids) == len(set(session_ids))

    # All should be valid UUIDs
    for session_id in session_ids:
        uuid.UUID(session_id)  # Should not raise


@pytest.mark.unit
def test_session_id_url_safe(session_manager):
    """Test that session IDs are URL-safe (no special encoding needed)."""
    session_id = session_manager.create_session()

    # UUID4 format: 8-4-4-4-12 hexadecimal digits with hyphens
    # Should only contain: 0-9, a-f, and hyphens
    allowed_chars = set('0123456789abcdef-')
    assert set(session_id).issubset(allowed_chars)

    # Should not need URL encoding
    import urllib.parse
    assert urllib.parse.quote(session_id, safe='') == session_id.replace('-', '%2D') or \
           urllib.parse.quote(session_id, safe='-') == session_id


@pytest.mark.unit
def test_construct_dashboard_url(session_manager):
    """Test constructing dashboard URL from session ID."""
    session_id = session_manager.create_session()

    # Test different server configurations
    test_cases = [
        ('localhost', 5000, f'http://localhost:5000/dashboard/{session_id}'),
        ('192.168.1.100', 5000, f'http://192.168.1.100:5000/dashboard/{session_id}'),
        ('example.com', 8080, f'http://example.com:8080/dashboard/{session_id}'),
    ]

    for host, port, expected_url in test_cases:
        url = f'http://{host}:{port}/dashboard/{session_id}'
        assert url == expected_url
        assert session_id in url
        assert '/dashboard/' in url


@pytest.mark.unit
def test_validate_session_id_format():
    """Test validation of session ID format using uuid.UUID()."""
    # Valid UUIDs
    valid_ids = [
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        '550e8400-e29b-41d4-a716-446655440000',
        '12345678-1234-4234-8234-123456789012',
    ]

    for session_id in valid_ids:
        try:
            uuid.UUID(session_id)
            is_valid = True
        except ValueError:
            is_valid = False
        assert is_valid, f"Expected {session_id} to be valid"

    # Invalid UUIDs
    invalid_ids = [
        'not-a-uuid',
        '12345',
        'abcd-efgh-ijkl-mnop',
        'a1b2c3d4-e5f6-7890-abcd',  # Too short
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890-extra',  # Too long
        '',
    ]

    for session_id in invalid_ids:
        try:
            uuid.UUID(session_id)
            is_valid = False  # Should have raised
        except (ValueError, AttributeError, TypeError):
            is_valid = True  # Correctly rejected
        assert is_valid, f"Expected {session_id} to be invalid"

    # Test None separately (raises TypeError)
    try:
        uuid.UUID(None)
        is_valid_none = False
    except (TypeError, AttributeError):
        is_valid_none = True
    assert is_valid_none, "Expected None to be invalid"


@pytest.mark.unit
def test_session_id_persistence_simulation(session_manager):
    """Test that session ID remains constant (simulating URL persistence)."""
    # Create session (monitor connects)
    session_id = session_manager.create_session()
    original_url = f'http://localhost:5000/dashboard/{session_id}'

    # Add setup data (monitor sends setup)
    setup = {'test': 'data'}
    timestamp = datetime.utcnow().isoformat()
    session_manager.update_setup(session_id, setup, timestamp)

    # Session ID should not change
    session = session_manager.get_session(session_id)
    assert session['session_id'] == session_id
    url_after_setup = f'http://localhost:5000/dashboard/{session["session_id"]}'
    assert url_after_setup == original_url

    # Add telemetry data (monitor sends telemetry)
    telemetry = {'lap': 1, 'fuel': 50.0}
    session_manager.update_telemetry(session_id, telemetry)

    # Session ID should still not change
    session = session_manager.get_session(session_id)
    assert session['session_id'] == session_id
    url_after_telemetry = f'http://localhost:5000/dashboard/{session["session_id"]}'
    assert url_after_telemetry == original_url


@pytest.mark.unit
def test_url_format_requirements():
    """Test that URL format meets all specification requirements."""
    session_id = str(uuid.uuid4())
    host = '192.168.1.100'
    port = 5000

    # Construct URL
    url = f'http://{host}:{port}/dashboard/{session_id}'

    # Test requirements from specification
    assert url.startswith('http://'), "URL should start with http://"
    assert '/dashboard/' in url, "URL should contain /dashboard/ path"
    assert session_id in url, "URL should contain session ID"
    assert len(session_id) == 36, "Session ID should be 36 characters"
    assert session_id.count('-') == 4, "Session ID should have 4 hyphens"

    # Test URL is shareable (no complex encoding needed)
    assert ' ' not in url, "URL should not contain spaces"
    assert '\n' not in url, "URL should not contain newlines"
    assert '\t' not in url, "URL should not contain tabs"


# ============================================================================
# Helper Method Tests
# ============================================================================

@pytest.mark.unit
def test_validate_session_id_valid():
    """Test session ID validation with valid UUIDs."""
    valid_uuids = [
        str(uuid.uuid4()),
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        '550e8400-e29b-41d4-a716-446655440000',
    ]

    for session_id in valid_uuids:
        is_valid, error = SessionManager.validate_session_id(session_id)
        assert is_valid is True, f"Expected {session_id} to be valid"
        assert error is None, f"Expected no error for {session_id}"


@pytest.mark.unit
def test_validate_session_id_invalid():
    """Test session ID validation with invalid inputs."""
    invalid_cases = [
        ('', "Session ID cannot be empty"),
        ('not-a-uuid', "Invalid UUID format"),
        ('12345', "Invalid UUID format"),
        ('a1b2c3d4-e5f6-7890-abcd', "Invalid UUID format"),  # Too short
    ]

    for session_id, expected_error_fragment in invalid_cases:
        is_valid, error = SessionManager.validate_session_id(session_id)
        assert is_valid is False, f"Expected {session_id} to be invalid"
        assert error is not None, f"Expected error message for {session_id}"
        assert expected_error_fragment.lower() in error.lower(), \
            f"Expected error to contain '{expected_error_fragment}' but got '{error}'"


@pytest.mark.unit
def test_validate_session_id_type_errors():
    """Test session ID validation with wrong types."""
    invalid_types = [None, 123, [], {}]

    for invalid_input in invalid_types:
        is_valid, error = SessionManager.validate_session_id(invalid_input)
        assert is_valid is False, f"Expected {invalid_input} to be invalid"
        assert error is not None


@pytest.mark.unit
def test_construct_dashboard_url_defaults():
    """Test dashboard URL construction with default parameters."""
    session_id = str(uuid.uuid4())
    url = SessionManager.construct_dashboard_url(session_id)

    # Should use defaults: localhost, port 5000, http
    assert url == f'http://localhost:5000/dashboard/{session_id}'


@pytest.mark.unit
def test_construct_dashboard_url_custom_params():
    """Test dashboard URL construction with custom parameters."""
    session_id = str(uuid.uuid4())

    # Test custom host and port
    url = SessionManager.construct_dashboard_url(
        session_id,
        host='192.168.1.100',
        port=8080
    )
    assert url == f'http://192.168.1.100:8080/dashboard/{session_id}'

    # Test HTTPS protocol
    url = SessionManager.construct_dashboard_url(
        session_id,
        host='example.com',
        port=443,
        protocol='https'
    )
    assert url == f'https://example.com:443/dashboard/{session_id}'


@pytest.mark.unit
def test_construct_dashboard_url_integration(session_manager):
    """Test URL construction with real session ID from SessionManager."""
    # Create real session
    session_id = session_manager.create_session()

    # Construct URL
    url = SessionManager.construct_dashboard_url(
        session_id,
        host='192.168.1.100',
        port=5000
    )

    # Verify structure
    assert session_id in url
    assert url.startswith('http://192.168.1.100:5000/dashboard/')
    assert len(url) > 40  # Host + path + UUID should be substantial

    # Verify session exists
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session['session_id'] == session_id
