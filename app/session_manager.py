"""
Session management for the 1Lap Dashboard Server.

Handles creation of unique session IDs, storage of session data
(setup and telemetry), and session lifecycle management.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class SessionManager:
    """
    Manages racing sessions with unique IDs and data storage.

    Attributes:
        _sessions: In-memory dictionary storing all active sessions
    """

    def __init__(self):
        """Initialize the SessionManager with empty session storage."""
        self._sessions: Dict[str, Dict] = {}

    def create_session(self) -> str:
        """
        Create a new session with a unique UUID.

        Returns:
            str: The newly created session ID (UUID4 format)
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'setup': None,
            'setup_timestamp': None,
            'telemetry': None,
            'last_update': None
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data by ID.

        Args:
            session_id: The UUID of the session to retrieve

        Returns:
            Dict containing session data, or None if session doesn't exist
        """
        return self._sessions.get(session_id)

    def update_setup(self, session_id: str, setup: Dict, timestamp: str) -> None:
        """
        Update the car setup data for a session.

        Args:
            session_id: The UUID of the session
            setup: Dictionary containing car setup data from REST API
            timestamp: ISO 8601 timestamp when setup was received

        Raises:
            KeyError: If session_id doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} does not exist")

        self._sessions[session_id]['setup'] = setup
        self._sessions[session_id]['setup_timestamp'] = timestamp

    def update_telemetry(self, session_id: str, telemetry: Dict) -> None:
        """
        Update the latest telemetry data for a session.

        Args:
            session_id: The UUID of the session
            telemetry: Dictionary containing latest telemetry data

        Raises:
            KeyError: If session_id doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} does not exist")

        self._sessions[session_id]['telemetry'] = telemetry
        self._sessions[session_id]['last_update'] = datetime.utcnow().isoformat()

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session from storage.

        Args:
            session_id: The UUID of the session to delete

        Note:
            Silently succeeds if session doesn't exist
        """
        self._sessions.pop(session_id, None)

    def get_active_sessions(self) -> List[str]:
        """
        Get list of all active session IDs.

        Returns:
            List of session ID strings (UUIDs)
        """
        return list(self._sessions.keys())
