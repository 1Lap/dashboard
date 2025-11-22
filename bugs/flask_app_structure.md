# Flask App Structure and Routes

**Date Created:** 2025-11-22
**Priority:** High
**Component:** Dashboard Server - Core
**Phase:** Phase 1 MVP

## Description

Set up Flask application factory pattern with proper structure, configuration, and HTTP routes for serving the dashboard.

## Requirements

### Must Have - App Factory
1. Flask app factory function (`create_app()`)
2. Flask-SocketIO initialization
3. Configuration loading from `config.py`
4. CORS configuration for WebSocket
5. Blueprint/route registration

### Must Have - HTTP Routes
1. `GET /` - Home page (server status)
2. `GET /dashboard/<session_id>` - Serve dashboard UI
3. Static file serving (CSS, JS, images)

### Must Have - Configuration
1. Environment-based config (dev/prod)
2. Secret key management
3. Debug mode toggle
4. Host/port configuration

### Nice to Have
1. Logging configuration
2. Error pages (404, 500)
3. Health check endpoint
4. Metrics endpoint

## Technical Details

**Directory Structure:**
```
server/
├── app/
│   ├── __init__.py          # App factory
│   ├── main.py              # Routes + WebSocket handlers
│   ├── session_manager.py   # Session management
│   └── models.py            # Data structures (future)
├── static/
│   ├── css/dashboard.css
│   ├── js/dashboard.js
│   └── img/logo.png
├── templates/
│   └── dashboard.html
├── tests/
├── run.py                   # Entry point
├── config.py                # Configuration
└── requirements.txt
```

**File:** `app/__init__.py`
```python
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize SocketIO with CORS
    socketio.init_app(app, cors_allowed_origins="*")

    # Import routes (after socketio init)
    from app import main

    return app
```

**File:** `run.py`
```python
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("1Lap Race Dashboard Server")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("Waiting for monitor connections...")
    print("=" * 60)

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

**File:** `config.py`
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
```

**File:** `app/main.py` (HTTP Routes)
```python
from flask import render_template, current_app

@current_app.route('/')
def index():
    """Home page - server status"""
    return "<h1>1Lap Race Dashboard Server</h1><p>Waiting for sessions...</p>"

@current_app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Serve dashboard for specific session"""
    return render_template('dashboard.html', session_id=session_id)
```

## Success Criteria

- [x] Flask app starts successfully
- [x] App factory pattern implemented
- [x] SocketIO initialized with CORS
- [x] Home route accessible at /
- [x] Dashboard route accessible at /dashboard/<id>
- [x] Static files served correctly
- [x] Configuration loads from environment
- [x] Debug mode works in development
- [ ] Unit tests pass (test_main.py)

## Testing

**Test File:** `tests/test_main.py`

**Test Cases:**
```python
def test_app_creation()                   # App factory works
def test_config_loading()                 # Config loads correctly
def test_home_route()                     # GET / returns 200
def test_dashboard_route()                # GET /dashboard/uuid returns 200
def test_dashboard_session_id()           # Session ID passed to template
def test_static_files()                   # CSS/JS accessible
def test_socketio_initialized()           # SocketIO attached to app
```

## Dependencies

**requirements.txt:**
```txt
flask>=2.3.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
eventlet>=0.33.0       # Async mode
gunicorn>=21.0.0       # Production server
```

## Environment Variables

**Development:**
```bash
export DEBUG=True
export SECRET_KEY=dev-secret-key
export HOST=0.0.0.0
export PORT=5000
```

**Production:**
```bash
export DEBUG=False
export SECRET_KEY=<random-secret-key>
export HOST=0.0.0.0
export PORT=5000
```

## Running the Server

**Development:**
```bash
python run.py
```

**Production (Gunicorn):**
```bash
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app
```

## Error Handling

**404 Not Found:**
- Future: Custom error page
- MVP: Flask default

**500 Internal Server Error:**
- Future: Custom error page + logging
- MVP: Flask default + console output

**WebSocket Errors:**
- Log and continue (don't crash server)
- See websocket_server.md for details

## Security Considerations

**Phase 1 MVP:**
- ⚠️ No authentication (secret URLs only)
- ⚠️ CORS open to all origins
- ⚠️ Debug mode enabled

**Future Improvements:**
- 🔒 Add session authentication
- 🔒 Restrict CORS to specific domains
- 🔒 Use HTTPS in production
- 🔒 Add rate limiting
- 🔒 Secure secret key management

## Related Files

- `app/main.py` - Routes and WebSocket handlers
- `app/session_manager.py` - Session management
- `run.py` - Server entry point
- `config.py` - Configuration
- `tests/test_main.py` - Route tests

## Deployment

**Local Network:**
```bash
# Run on driver's PC
python run.py
# Access: http://<driver-ip>:5000/dashboard/<session-id>
```

**Cloud (Heroku Example):**
```bash
# Create Procfile
echo "web: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app" > Procfile

# Deploy
git push heroku main
```

See RACE_DASHBOARD_PLAN.md lines 1381-1471 for detailed deployment options.

## References

- RACE_DASHBOARD_PLAN.md - Lines 404-531 (Flask app implementation)
- RACE_DASHBOARD_PLAN.md - Lines 1381-1471 (Deployment options)
- Flask docs: https://flask.palletsprojects.com/
- Flask-SocketIO docs: https://flask-socketio.readthedocs.io/
