"""
HTTP routes and WebSocket handlers for 1Lap Dashboard Server.

Provides HTTP endpoints for the home page and dashboard views,
as well as WebSocket event handlers for real-time communication.
"""

from flask import render_template
from flask_socketio import emit, join_room
from app.session_manager import SessionManager
import logging
from pathlib import Path
import json

# Optional schema validation (enabled if jsonschema is available)
try:
    from jsonschema import Draft202012Validator, ValidationError
    JSONSCHEMA_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    JSONSCHEMA_AVAILABLE = False

SCHEMA_VALIDATORS = {}
VALIDATION_ENABLED = False

def _load_schema_validators():
    global SCHEMA_VALIDATORS, VALIDATION_ENABLED
    if not JSONSCHEMA_AVAILABLE:
        return

    # Resolve schemas directory within dashboard repo: dashboard/bugs/schemas/
    schemas_dir = Path(__file__).resolve().parents[1] / 'bugs' / 'schemas'
    telemetry_schema_path = schemas_dir / 'telemetry_update.schema.json'
    setup_schema_path = schemas_dir / 'setup_data.schema.json'

    try:
        with telemetry_schema_path.open('r', encoding='utf-8') as f:
            telemetry_schema = json.load(f)
        with setup_schema_path.open('r', encoding='utf-8') as f:
            setup_schema = json.load(f)

        SCHEMA_VALIDATORS['telemetry_update'] = Draft202012Validator(telemetry_schema)
        SCHEMA_VALIDATORS['setup_data'] = Draft202012Validator(setup_schema)
        VALIDATION_ENABLED = True
    except Exception:
        # If loading fails, leave validation disabled but keep server running
        VALIDATION_ENABLED = False

# Configure logging
logger = logging.getLogger(__name__)

# Create a global session manager instance
session_manager = SessionManager()


def register_routes(app):
    """
    Register HTTP routes with the Flask application.

    Args:
        app: Flask application instance
    """

    @app.route('/')
    def index():
        """
        Home page - server status.

        Returns:
            str: HTML response showing server status
        """
        return """
        <html>
            <head>
                <title>1Lap Race Dashboard Server</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    h1 {
                        color: #333;
                    }
                    .info {
                        background-color: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                </style>
            </head>
            <body>
                <h1>1Lap Race Dashboard Server</h1>
                <div class="info">
                    <p>Server is running and waiting for monitor connections...</p>
                    <p>Dashboard URLs will be generated when a monitor connects.</p>
                </div>
            </body>
        </html>
        """

    @app.route('/dashboard/<session_id>')
    def dashboard(session_id):
        """
        Serve dashboard for specific session.

        Args:
            session_id: UUID of the racing session

        Returns:
            str: Rendered dashboard HTML template
        """
        return render_template('dashboard.html', session_id=session_id)


def register_socketio_handlers(socketio):
    """
    Register WebSocket event handlers with SocketIO instance.

    Args:
        socketio: Flask-SocketIO instance

    Event handlers registered:
        - connect: Client connects to server
        - disconnect: Client disconnects from server
        - request_session_id: Monitor requests new session ID
        - setup_data: Monitor sends car setup data
        - telemetry_update: Monitor sends telemetry updates (2Hz)
        - join_session: Dashboard joins session room
    """

    @socketio.on('connect')
    def handle_connect():
        """
        Handle client connection to WebSocket server.

        Logs connection and returns success status.
        """
        logger.info(f"Client connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        """
        Handle client disconnection from WebSocket server.

        Logs disconnection.
        """
        logger.info(f"Client disconnected")

    @socketio.on('request_session_id')
    def handle_request_session_id(data=None):
        """
        Handle monitor request for new session ID.

        Args:
            data: Optional data payload (not used, but required by Flask-SocketIO)

        Flow:
            1. Create new session in SessionManager
            2. Emit 'session_id_assigned' event to monitor with UUID

        Emits:
            session_id_assigned: {'session_id': str} to requesting client
        """
        # Create new session
        session_id = session_manager.create_session()
        logger.info(f"Created new session: {session_id}")

        # Send session ID to monitor
        emit('session_id_assigned', {'session_id': session_id})

    @socketio.on('setup_data')
    def handle_setup_data(data):
        """
        Handle car setup data from monitor.

        Args:
            data: dict containing:
                - session_id: str (UUID)
                - timestamp: str (ISO 8601)
                - setup: dict (car setup from REST API)

        Flow:
            1. Validate session exists
            2. Store setup in SessionManager
            3. Broadcast 'setup_update' to all dashboards in session room

        Emits:
            setup_update: Setup data to all clients in session room
        """
        # Validate against schema if enabled
        if VALIDATION_ENABLED:
            try:
                SCHEMA_VALIDATORS['setup_data'].validate(data)
            except Exception as e:
                logger.warning(f"Invalid setup_data payload rejected: {e}")
                return

        session_id = data.get('session_id')
        timestamp = data.get('timestamp')
        setup = data.get('setup')

        # Validate session exists
        if not session_id or not session_manager.get_session(session_id):
            logger.warning(f"Setup data received for invalid session: {session_id}")
            return

        try:
            # Store setup in session
            session_manager.update_setup(session_id, setup, timestamp)
            logger.info(f"Stored setup for session {session_id}")

            # Broadcast to all dashboards in room
            emit('setup_update', {
                'session_id': session_id,
                'timestamp': timestamp,
                'setup': setup
            }, room=session_id)

        except Exception as e:
            logger.error(f"Error handling setup data: {str(e)}")

    @socketio.on('telemetry_update')
    def handle_telemetry_update(data):
        """
        Handle telemetry update from monitor (2Hz rate).

        Args:
            data: dict containing:
                - session_id: str (UUID)
                - telemetry: dict (real-time telemetry data)

        Flow:
            1. Validate session exists
            2. Store telemetry in SessionManager
            3. Broadcast 'telemetry_update' to all dashboards in session room

        Emits:
            telemetry_update: Telemetry data to all clients in session room
        """
        # Validate against schema if enabled
        if VALIDATION_ENABLED:
            try:
                SCHEMA_VALIDATORS['telemetry_update'].validate(data)
            except Exception as e:
                logger.warning(f"Invalid telemetry_update payload rejected: {e}")
                return

        session_id = data.get('session_id')
        telemetry = data.get('telemetry')

        # Validate session exists
        if not session_id or not session_manager.get_session(session_id):
            logger.warning(f"Telemetry received for invalid session: {session_id}")
            return

        try:
            # Store telemetry in session
            session_manager.update_telemetry(session_id, telemetry)
            logger.debug(f"Updated telemetry for session {session_id}")

            # Broadcast to all dashboards in room
            emit('telemetry_update', {
                'session_id': session_id,
                'telemetry': telemetry
            }, room=session_id)

        except Exception as e:
            logger.error(f"Error handling telemetry: {str(e)}")

    @socketio.on('join_session')
    def handle_join_session(data):
        """
        Handle dashboard joining a session room.

        Args:
            data: dict containing:
                - session_id: str (UUID)

        Flow:
            1. Validate session_id is present and valid
            2. Add client to session room
            3. Send current setup (if available)
            4. Send current telemetry (if available)

        Emits:
            setup_update: Current setup (if exists) to joining client
            telemetry_update: Current telemetry (if exists) to joining client
        """
        session_id = data.get('session_id')

        # Validate session_id present
        if not session_id:
            logger.warning("Dashboard tried to join without session_id")
            return

        # Validate session exists
        session = session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Dashboard tried to join non-existent session: {session_id}")
            return

        # Add client to session room
        join_room(session_id)
        logger.info(f"Dashboard joined session: {session_id}")

        # Send current setup if available
        if session.get('setup'):
            emit('setup_update', {
                'session_id': session_id,
                'timestamp': session['setup_timestamp'],
                'setup': session['setup']
            })

        # Send current telemetry if available
        if session.get('telemetry'):
            emit('telemetry_update', {
                'session_id': session_id,
                'telemetry': session['telemetry']
            })

# Initialize schema validators at import time
_load_schema_validators()
