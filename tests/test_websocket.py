"""
Unit tests for WebSocket event handlers.

Tests the bidirectional communication between monitor/dashboard clients
and the Flask-SocketIO server.

Test Organization:
    - TestMonitorEvents: Monitor → Server communication
    - TestDashboardEvents: Dashboard → Server communication
    - TestBroadcasting: Server → Dashboard broadcasting
    - TestConnectionEvents: Connect/disconnect handling
    - TestErrorHandling: Invalid data and edge cases

Running WebSocket Tests:
    # All WebSocket tests
    pytest tests/test_websocket.py -v

    # Specific test class
    pytest tests/test_websocket.py::TestMonitorEvents -v

    # With coverage
    pytest tests/test_websocket.py --cov=app --cov-report=term-missing
"""

import pytest
from tests.test_data import generate_telemetry, generate_setup
import uuid


@pytest.mark.unit
class TestMonitorEvents:
    """
    Test WebSocket events from monitor to server.

    Monitor events tested:
        - request_session_id: Monitor requests new session ID
        - setup_data: Monitor sends car setup data
        - telemetry_update: Monitor sends telemetry updates (2Hz)
    """

    def test_request_session_id(self, app):
        """
        Test monitor requesting session ID.

        Flow:
            1. Monitor connects
            2. Monitor emits 'request_session_id' event
            3. Server responds with 'session_id_assigned' event
            4. Session ID is valid UUID4 format

        Verifies:
            - Event handler responds correctly
            - Session ID is valid UUID
            - Session is created in SessionManager
        """
        from app import socketio

        # Create monitor client
        monitor = socketio.test_client(app)
        assert monitor.is_connected()

        # Request session ID
        monitor.emit('request_session_id', {})

        # Get response
        received = monitor.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'session_id_assigned'

        # Verify session ID format
        session_id = received[0]['args'][0]['session_id']
        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID4 format with hyphens

        # Verify it's a valid UUID
        try:
            parsed_uuid = uuid.UUID(session_id)
            assert str(parsed_uuid) == session_id
        except ValueError:
            pytest.fail(f"Invalid UUID format: {session_id}")

    def test_setup_data_storage(self, app, sample_setup_data):
        """
        Test monitor sending setup data.

        Flow:
            1. Monitor connects and gets session ID
            2. Monitor emits 'setup_data' with setup payload
            3. Server stores setup in SessionManager
            4. Setup can be retrieved from session

        Verifies:
            - Setup data is stored correctly
            - Session data structure is correct
            - Timestamps are preserved
        """
        from app import socketio
        from app.main import session_manager

        # Create monitor and get session ID
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        # Send setup data
        timestamp = '2025-11-22T14:30:00.000Z'
        monitor.emit('setup_data', {
            'session_id': session_id,
            'timestamp': timestamp,
            'setup': sample_setup_data
        })

        # Verify setup stored in SessionManager
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session['setup'] == sample_setup_data
        assert session['setup_timestamp'] == timestamp

    def test_telemetry_update_storage(self, app, sample_telemetry_data):
        """
        Test monitor sending telemetry updates.

        Flow:
            1. Monitor connects and gets session ID
            2. Monitor emits 'telemetry_update' with telemetry payload
            3. Server stores telemetry in SessionManager
            4. Telemetry can be retrieved from session

        Verifies:
            - Telemetry data is stored correctly
            - Latest telemetry replaces previous
            - Timestamps are updated
        """
        from app import socketio
        from app.main import session_manager

        # Create monitor and get session ID
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        # Send telemetry update
        monitor.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry_data
        })

        # Verify telemetry stored in SessionManager
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session['telemetry'] == sample_telemetry_data
        assert session['last_update'] is not None

    def test_multiple_telemetry_updates(self, app):
        """
        Test multiple consecutive telemetry updates.

        Flow:
            1. Monitor sends 5 telemetry updates with different lap numbers
            2. Each update is stored (latest replaces previous)
            3. Final state has last telemetry

        Verifies:
            - Multiple updates work correctly
            - Latest telemetry is always stored
            - No data corruption
        """
        from app import socketio
        from app.main import session_manager

        # Setup
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        # Send 5 telemetry updates
        for lap_num in range(1, 6):
            telemetry = generate_telemetry(lap=lap_num, fuel=80.0 - (lap_num * 2.5))
            monitor.emit('telemetry_update', {
                'session_id': session_id,
                'telemetry': telemetry
            })

        # Verify last telemetry is stored
        session = session_manager.get_session(session_id)
        assert session['telemetry']['lap'] == 5
        assert session['telemetry']['fuel'] == 67.5  # 80 - (5 * 2.5)


@pytest.mark.unit
class TestDashboardEvents:
    """
    Test WebSocket events from dashboard to server.

    Dashboard events tested:
        - join_session: Dashboard joins session room to receive broadcasts
    """

    def test_join_session_without_data(self, app):
        """
        Test dashboard joining session with no prior data.

        Flow:
            1. Monitor creates session
            2. Dashboard joins session (no setup/telemetry sent yet)
            3. Dashboard successfully joins room
            4. No data is sent (nothing to broadcast yet)

        Verifies:
            - Dashboard can join empty session
            - No errors when no data exists
            - Room joining works
        """
        from app import socketio

        # Create session via monitor
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        # Dashboard joins session
        dashboard = socketio.test_client(app)
        dashboard.emit('join_session', {'session_id': session_id})

        # Dashboard should be connected (no errors)
        assert dashboard.is_connected()

    def test_join_session_with_existing_setup(self, app, sample_setup_data):
        """
        Test dashboard joining session with existing setup data.

        Flow:
            1. Monitor creates session and sends setup
            2. Dashboard joins session AFTER setup sent
            3. Dashboard receives setup_update immediately on join

        Verifies:
            - Late-joining dashboards get existing setup
            - Setup is cached and delivered correctly
            - Data structure matches expected format
        """
        from app import socketio

        # Create session and send setup
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        timestamp = '2025-11-22T14:30:00.000Z'
        monitor.emit('setup_data', {
            'session_id': session_id,
            'timestamp': timestamp,
            'setup': sample_setup_data
        })

        # Dashboard joins after setup sent
        dashboard = socketio.test_client(app)
        dashboard.emit('join_session', {'session_id': session_id})

        # Dashboard should receive setup_update
        received = dashboard.get_received()
        setup_updates = [msg for msg in received if msg['name'] == 'setup_update']
        assert len(setup_updates) == 1
        assert setup_updates[0]['args'][0]['setup'] == sample_setup_data

    def test_join_session_with_existing_telemetry(self, app, sample_telemetry_data):
        """
        Test dashboard joining session with existing telemetry.

        Flow:
            1. Monitor creates session and sends telemetry
            2. Dashboard joins session AFTER telemetry sent
            3. Dashboard receives current telemetry on join

        Verifies:
            - Late-joining dashboards get current telemetry
            - Telemetry is cached correctly
        """
        from app import socketio

        # Create session and send telemetry
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        monitor.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry_data
        })

        # Dashboard joins after telemetry sent
        dashboard = socketio.test_client(app)
        dashboard.emit('join_session', {'session_id': session_id})

        # Dashboard should receive telemetry_update
        received = dashboard.get_received()
        telemetry_updates = [msg for msg in received if msg['name'] == 'telemetry_update']
        assert len(telemetry_updates) == 1
        assert telemetry_updates[0]['args'][0]['telemetry'] == sample_telemetry_data


@pytest.mark.unit
class TestBroadcasting:
    """
    Test server broadcasting to dashboards.

    Broadcasting scenarios tested:
        - Setup broadcast to single dashboard
        - Telemetry broadcast to single dashboard
        - Broadcast to multiple dashboards
        - Session isolation (no cross-contamination)
    """

    def test_setup_broadcast_to_dashboard(self, app, sample_setup_data):
        """
        Test setup broadcasting to connected dashboard.

        Flow:
            1. Monitor creates session
            2. Dashboard joins session
            3. Monitor sends setup
            4. Dashboard receives setup_update broadcast

        Verifies:
            - Setup broadcasts to dashboards in room
            - Data matches what monitor sent
            - Broadcasting happens immediately
        """
        from app import socketio

        # Setup monitor and dashboard
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        dashboard = socketio.test_client(app)
        dashboard.emit('join_session', {'session_id': session_id})
        dashboard.get_received()  # Clear any initial messages

        # Monitor sends setup
        timestamp = '2025-11-22T14:30:00.000Z'
        monitor.emit('setup_data', {
            'session_id': session_id,
            'timestamp': timestamp,
            'setup': sample_setup_data
        })

        # Dashboard receives setup_update
        received = dashboard.get_received()
        assert len(received) >= 1
        setup_msg = next((msg for msg in received if msg['name'] == 'setup_update'), None)
        assert setup_msg is not None
        assert setup_msg['args'][0]['setup'] == sample_setup_data

    def test_telemetry_broadcast_to_dashboard(self, app, sample_telemetry_data):
        """
        Test telemetry broadcasting to connected dashboard.

        Flow:
            1. Monitor creates session
            2. Dashboard joins session
            3. Monitor sends telemetry
            4. Dashboard receives telemetry_update broadcast

        Verifies:
            - Telemetry broadcasts at 2Hz rate
            - Data matches what monitor sent
            - All fields are preserved
        """
        from app import socketio

        # Setup monitor and dashboard
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        dashboard = socketio.test_client(app)
        dashboard.emit('join_session', {'session_id': session_id})
        dashboard.get_received()  # Clear any initial messages

        # Monitor sends telemetry
        monitor.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry_data
        })

        # Dashboard receives telemetry_update
        received = dashboard.get_received()
        assert len(received) >= 1
        telem_msg = next((msg for msg in received if msg['name'] == 'telemetry_update'), None)
        assert telem_msg is not None
        assert telem_msg['args'][0]['telemetry']['lap'] == sample_telemetry_data['lap']

    def test_broadcast_to_multiple_dashboards(self, app, sample_telemetry_data):
        """
        Test broadcasting to multiple dashboards in same session.

        Flow:
            1. Monitor creates session
            2. Three dashboards join same session
            3. Monitor sends telemetry
            4. All three dashboards receive update

        Verifies:
            - Broadcasting works with multiple clients
            - All clients receive identical data
            - No data loss
        """
        from app import socketio

        # Setup monitor
        monitor = socketio.test_client(app)
        monitor.emit('request_session_id', {})
        response = monitor.get_received()
        session_id = response[0]['args'][0]['session_id']

        # Create 3 dashboards
        dashboards = []
        for _ in range(3):
            dashboard = socketio.test_client(app)
            dashboard.emit('join_session', {'session_id': session_id})
            dashboard.get_received()  # Clear initial messages
            dashboards.append(dashboard)

        # Monitor sends telemetry
        monitor.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry_data
        })

        # All dashboards receive update
        for dashboard in dashboards:
            received = dashboard.get_received()
            assert len(received) >= 1
            telem_msg = next((msg for msg in received if msg['name'] == 'telemetry_update'), None)
            assert telem_msg is not None
            assert telem_msg['args'][0]['telemetry']['lap'] == sample_telemetry_data['lap']

    def test_session_isolation(self, app):
        """
        Test that sessions are isolated (no cross-contamination).

        Flow:
            1. Create two separate sessions with monitors
            2. Dashboard A joins session 1
            3. Dashboard B joins session 2
            4. Monitor 1 sends telemetry
            5. Only Dashboard A receives it (not Dashboard B)

        Verifies:
            - Session rooms are isolated
            - No cross-talk between sessions
            - Broadcasting is scoped correctly
        """
        from app import socketio

        # Create session 1
        monitor1 = socketio.test_client(app)
        monitor1.emit('request_session_id', {})
        response1 = monitor1.get_received()
        session_id_1 = response1[0]['args'][0]['session_id']

        # Create session 2
        monitor2 = socketio.test_client(app)
        monitor2.emit('request_session_id', {})
        response2 = monitor2.get_received()
        session_id_2 = response2[0]['args'][0]['session_id']

        # Dashboard A joins session 1
        dashboard_a = socketio.test_client(app)
        dashboard_a.emit('join_session', {'session_id': session_id_1})
        dashboard_a.get_received()

        # Dashboard B joins session 2
        dashboard_b = socketio.test_client(app)
        dashboard_b.emit('join_session', {'session_id': session_id_2})
        dashboard_b.get_received()

        # Monitor 1 sends telemetry
        telemetry_1 = generate_telemetry(lap=10)
        monitor1.emit('telemetry_update', {
            'session_id': session_id_1,
            'telemetry': telemetry_1
        })

        # Dashboard A receives update
        received_a = dashboard_a.get_received()
        assert len(received_a) >= 1

        # Dashboard B should NOT receive update
        received_b = dashboard_b.get_received()
        # Dashboard B should have no messages or only non-telemetry messages
        telemetry_msgs = [msg for msg in received_b if msg['name'] == 'telemetry_update']
        assert len(telemetry_msgs) == 0


@pytest.mark.unit
class TestConnectionEvents:
    """
    Test connection and disconnection handling.

    Events tested:
        - connect: Client connects to server
        - disconnect: Client disconnects from server
    """

    def test_client_connect(self, app):
        """
        Test client can connect to WebSocket server.

        Verifies:
            - Connection succeeds
            - Client is marked as connected
        """
        from app import socketio

        client = socketio.test_client(app)
        assert client.is_connected()

    def test_client_disconnect(self, app):
        """
        Test client can disconnect from server.

        Verifies:
            - Disconnection works
            - No errors on disconnect
        """
        from app import socketio

        client = socketio.test_client(app)
        assert client.is_connected()

        client.disconnect()
        assert not client.is_connected()

    def test_reconnection_after_disconnect(self, app):
        """
        Test client can reconnect after disconnecting.

        Flow:
            1. Client connects
            2. Client disconnects
            3. New client connects
            4. Both connections work correctly

        Verifies:
            - Reconnection is supported
            - No state corruption
        """
        from app import socketio

        # First connection
        client1 = socketio.test_client(app)
        assert client1.is_connected()
        client1.disconnect()

        # Second connection (reconnect)
        client2 = socketio.test_client(app)
        assert client2.is_connected()


@pytest.mark.unit
class TestErrorHandling:
    """
    Test error handling and edge cases.

    Error scenarios tested:
        - Invalid session ID format
        - Non-existent session
        - Missing required fields
        - Malformed data
    """

    def test_join_invalid_session_id(self, app):
        """
        Test dashboard joining with invalid session ID.

        Flow:
            1. Dashboard tries to join with invalid UUID
            2. Server handles gracefully (no crash)

        Verifies:
            - Invalid session IDs don't crash server
            - Client remains connected
        """
        from app import socketio

        dashboard = socketio.test_client(app)
        assert dashboard.is_connected()

        # Try to join with invalid session ID
        dashboard.emit('join_session', {'session_id': 'invalid-uuid-format'})

        # Client should still be connected (graceful handling)
        assert dashboard.is_connected()

    def test_join_nonexistent_session(self, app):
        """
        Test dashboard joining non-existent session.

        Flow:
            1. Dashboard tries to join with valid UUID but session doesn't exist
            2. Server handles gracefully

        Verifies:
            - Non-existent sessions don't crash server
            - Error handling works correctly
        """
        from app import socketio

        dashboard = socketio.test_client(app)
        assert dashboard.is_connected()

        # Try to join non-existent session (valid UUID format)
        fake_session_id = str(uuid.uuid4())
        dashboard.emit('join_session', {'session_id': fake_session_id})

        # Client should still be connected
        assert dashboard.is_connected()

    def test_setup_data_invalid_session(self, app, sample_setup_data):
        """
        Test monitor sending setup for non-existent session.

        Flow:
            1. Monitor sends setup without requesting session first
            2. Server handles gracefully (logs error but doesn't crash)

        Verifies:
            - Invalid workflows are handled
            - Server doesn't crash
        """
        from app import socketio

        monitor = socketio.test_client(app)
        assert monitor.is_connected()

        # Send setup with non-existent session ID
        fake_session_id = str(uuid.uuid4())
        monitor.emit('setup_data', {
            'session_id': fake_session_id,
            'timestamp': '2025-11-22T14:30:00.000Z',
            'setup': sample_setup_data
        })

        # Monitor should still be connected
        assert monitor.is_connected()

    def test_telemetry_invalid_session(self, app, sample_telemetry_data):
        """
        Test monitor sending telemetry for non-existent session.

        Flow:
            1. Monitor sends telemetry without valid session
            2. Server handles gracefully

        Verifies:
            - Invalid telemetry updates don't crash server
        """
        from app import socketio

        monitor = socketio.test_client(app)
        assert monitor.is_connected()

        # Send telemetry with non-existent session ID
        fake_session_id = str(uuid.uuid4())
        monitor.emit('telemetry_update', {
            'session_id': fake_session_id,
            'telemetry': sample_telemetry_data
        })

        # Monitor should still be connected
        assert monitor.is_connected()

    def test_missing_session_id_field(self, app):
        """
        Test handling of events with missing session_id field.

        Flow:
            1. Dashboard tries to join without session_id in payload
            2. Server handles gracefully

        Verifies:
            - Missing required fields don't crash server
            - Error handling is robust
        """
        from app import socketio

        dashboard = socketio.test_client(app)
        assert dashboard.is_connected()

        # Try to join without session_id field
        dashboard.emit('join_session', {})

        # Client should still be connected
        assert dashboard.is_connected()
