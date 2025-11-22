"""
Unit tests for SessionManager class.

Tests session creation, data storage, and retrieval.
"""

import pytest
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
