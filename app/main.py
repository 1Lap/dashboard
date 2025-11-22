"""
HTTP routes and WebSocket handlers for 1Lap Dashboard Server.

Provides HTTP endpoints for the home page and dashboard views,
as well as WebSocket event handlers for real-time communication.
"""

from flask import render_template
from app.session_manager import SessionManager

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


# WebSocket event handlers will be added in the websocket_server feature
# For now, this file provides the HTTP routes only
