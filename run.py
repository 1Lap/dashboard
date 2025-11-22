"""
Development server entry point for 1Lap Dashboard Server.

Run this file directly to start the Flask development server with SocketIO support.
For production, use gunicorn instead (see deployment configuration).
"""

from app import create_app, socketio
from config import Config

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("1Lap Race Dashboard Server")
    print("=" * 60)
    print(f"Server running at: http://{Config.HOST}:{Config.PORT}")
    print("Waiting for monitor connections...")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop the server")
    print()

    # Run the Flask app with SocketIO support
    # debug=True enables auto-reload and better error messages
    # host and port are loaded from config
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
