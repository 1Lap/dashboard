# 1Lap Dashboard Server - Claude Instructions

## Project Overview

This is the **1Lap Race Dashboard Server** - a Flask-based WebSocket server that receives real-time telemetry from a monitor (running on Windows with LMU) and broadcasts it to web-based dashboards accessible by endurance racing team members.

**Current Status**: ✅ Phase 1 MVP Complete - All 6 core features implemented and tested (94% coverage, 62 tests passing)

**Purpose**: During endurance races, team members need to monitor car telemetry (fuel, tire temps/pressures, setup) without distracting the driver. This server provides a central hub that receives telemetry and serves it to multiple web dashboards via secret URLs.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LMU (Windows)                           │
│  ┌─────────────────┐              ┌────────────────────┐       │
│  │ Shared Memory   │              │   REST API         │       │
│  │ (Telemetry)     │              │   (localhost:6397) │       │
│  └────────┬────────┘              └─────────┬──────────┘       │
└───────────┼─────────────────────────────────┼──────────────────┘
            │                                 │
            └────────────┬────────────────────┘
                         ▼
            ┌─────────────────────────┐
            │   monitor (Python)      │  ← Separate repo
            │   - Reads shared memory │
            │   - Reads REST API      │
            │   - Publishes to server │
            └────────────┬────────────┘
                         │ WebSocket (2Hz)
                         ▼
            ┌─────────────────────────┐
            │   server (Flask)        │  ← THIS REPO
            │   - Session manager     │
            │   - WebSocket broadcast │
            │   - Serves dashboard UI │
            └────────────┬────────────┘
                         │ WebSocket (bidirectional)
                         ▼
            ┌─────────────────────────┐
            │   Web Browser           │
            │   - Dashboard UI        │
            │   - Auto-updating       │
            │   - Mobile responsive   │
            └─────────────────────────┘
```

## Three-Repository Architecture

| Repository | Purpose | Status |
|------------|---------|--------|
| **monitor** | Data collector (fork of writer) | Planned |
| **server** | Dashboard web service (Flask) | **THIS REPO** - ✅ MVP Complete |
| **writer** | CSV telemetry logger | Complete (archived in _archive/) |

## Development Philosophy

### Test-Driven Development (TDD)
- **ALWAYS write tests before code** when implementing new features
- Tests should fail first, then write code to make them pass
- Target coverage: **80%+ on core modules**
- If tests can't pass after trying, ask user before modifying tests

### Feature-First Development
- Each feature is fully specified in `bugs/` directory before implementation
- Follow the implementation order in `bugs/README.md`
- Mark features complete as you implement them
- Update bug files when resolving issues

## Project Structure

```
server/
├── .claude/
│   └── CLAUDE.md                    # This file
├── bugs/
│   ├── README.md                    # Feature index & status
│   ├── session_management.md        # Session & UUID management
│   ├── flask_app_structure.md       # App factory & routes
│   ├── websocket_server.md          # WebSocket communication
│   ├── dashboard_ui_frontend.md     # HTML/CSS/JS frontend
│   ├── secret_url_generation.md     # Session URL handling
│   ├── testing_infrastructure.md    # Test setup & specs
│   ├── error_handling_reconnection.md  # Reliability features
│   ├── deployment_configuration.md  # Local/cloud deployment
│   └── documentation_and_readme.md  # Docs templates
├── app/
│   ├── __init__.py                  # Flask app factory
│   ├── main.py                      # Routes + WebSocket handlers
│   ├── session_manager.py           # Session management
│   └── models.py                    # Data structures (future)
├── static/
│   ├── css/dashboard.css            # Dashboard styles
│   ├── js/dashboard.js              # WebSocket client + UI
│   └── img/logo.png                 # Assets
├── templates/
│   └── dashboard.html               # Dashboard UI template
├── tests/
│   ├── conftest.py                  # Shared fixtures
│   ├── test_session_manager.py      # SessionManager tests
│   ├── test_main.py                 # Route tests
│   ├── test_websocket.py            # WebSocket tests
│   ├── test_integration.py          # E2E tests
│   └── test_data.py                 # Test data generators
├── run.py                           # Development server entry point
├── config.py                        # Server configuration
├── gunicorn_config.py               # Production server config
├── requirements.txt                 # Dependencies
├── requirements-dev.txt             # Testing dependencies
├── pytest.ini                       # Test configuration
├── Dockerfile                       # Container config (optional)
├── docker-compose.yml               # Container orchestration (optional)
├── Procfile                         # Heroku deployment (optional)
├── README.md                        # Project README
├── RACE_DASHBOARD_PLAN.md           # Complete implementation plan
├── PROJECT_STATUS.md                # Implementation progress tracker
└── _archive/                        # Archived writer project code
```

## Core Components (✅ IMPLEMENTED)

### 1. SessionManager (`app/session_manager.py`) ✅ COMPLETE
- Generate unique session IDs (UUID4)
- Store session data (setup + telemetry)
- Support multiple concurrent sessions
- URL validation and construction helpers
- **Spec:** `bugs/session_management.md`
- **Tests:** 21 passing, 93% coverage

### 2. Flask App (`app/__init__.py`, `app/main.py`) ✅ COMPLETE
- App factory pattern
- HTTP routes: `/` (home), `/dashboard/<session_id>` (dashboard)
- Static file serving
- Configuration management
- **Spec:** `bugs/flask_app_structure.md`
- **Tests:** 12 passing, 100% coverage

### 3. WebSocket Server (`app/main.py`) ✅ COMPLETE
- Monitor → Server communication
  - `request_session_id` → `session_id_assigned`
  - `setup_data` (once per session)
  - `telemetry_update` (2Hz)
- Dashboard → Server communication
  - `join_session` → room joined
- Server → Dashboard broadcasting
  - `setup_update` (on join + when received)
  - `telemetry_update` (2Hz)
- Room-based broadcasting (one room per session)
- **Spec:** `bugs/websocket_server.md`
- **Tests:** 19 unit + 10 integration passing, 94% coverage

### 4. Dashboard UI (`templates/dashboard.html`, `static/`) ✅ COMPLETE
- Single-page web application
- Real-time telemetry display
  - Session info (driver, car, track, position, lap)
  - Fuel (liters, %, estimated laps remaining)
  - Tire temperatures (FL, FR, RL, RR)
  - Tire pressures (FL, FR, RL, RR)
  - Brake temperatures
  - Engine temperature
  - Weather (track + ambient temps)
- Car setup display (JSON from REST API)
- Connection status indicator
- Mobile responsive design
- **Spec:** `bugs/dashboard_ui_frontend.md`
- **Tests:** Manual testing complete

### 5. Testing Infrastructure (`tests/`) ✅ COMPLETE
- pytest configuration (pytest.ini)
- Unit tests (SessionManager, routes, WebSocket)
- Integration tests (E2E flow)
- Test fixtures and data generators
- Coverage reporting (94% achieved, exceeds 80% target)
- GitHub Actions CI/CD workflow
- **Spec:** `bugs/testing_infrastructure.md`
- **Tests:** 62 passing (33 unit + 10 integration + 19 WebSocket)

## Implementation Phases

### Phase 1: MVP (Core Functionality) ✅ COMPLETE
**Completed:** 2025-11-22
**Features:** (See `bugs/README.md` for details)
1. Session Management ✅ COMPLETE
2. Flask App Structure ✅ COMPLETE
3. WebSocket Server ✅ COMPLETE
4. Dashboard UI Frontend ✅ COMPLETE
5. Secret URL Generation ✅ COMPLETE
6. Testing Infrastructure ✅ COMPLETE

**Success Criteria:** ✅ All Met
- ✅ Monitor connects and receives session ID
- ✅ Monitor publishes setup + telemetry (2Hz)
- ✅ Dashboard loads at secret URL
- ✅ Dashboard displays real-time telemetry
- ✅ Multiple dashboards can view same session
- ✅ Mobile responsive UI
- ✅ 94% test coverage (exceeds 80% target)
- ✅ All 62 unit/integration tests passing

### Phase 2: Polish & Deployment - ~1 week
**Features:**
7. Error Handling & Reconnection 🔶 MEDIUM PRIORITY
8. Deployment Configuration 🔶 MEDIUM PRIORITY
9. Documentation & README 🔶 MEDIUM PRIORITY

**Success Criteria:**
- Auto-reconnection works (monitor + dashboard)
- Error handling graceful (no crashes)
- Documentation complete
- Can deploy to local network
- Can deploy to cloud (Heroku/Railway)

## Technology Stack

**Backend:**
- Python 3.11+
- Flask 2.3+ (web framework)
- Flask-SocketIO 5.3+ (WebSocket support)
- python-socketio 5.9+ (client library)
- eventlet (async mode)
- gunicorn (production server)

**Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript (no framework for MVP)
- Socket.IO client (CDN)

**Testing:**
- pytest 7.4+
- pytest-cov 4.1+ (coverage)
- pytest-flask 1.2+ (Flask testing)

**Deployment:**
- Local: Python built-in server
- Production: Gunicorn + eventlet
- Optional: Docker, Heroku, Railway

## Testing Requirements

### Running Tests
```bash
# All tests
pytest -v

# Specific module
pytest tests/test_session_manager.py -v

# With coverage
pytest --cov=app --cov-report=html

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration
```

### Test Organization
- Each module has corresponding test file: `test_<module>.py`
- Use pytest fixtures for setup/teardown (see `tests/conftest.py`)
- Mock WebSocket clients for testing
- Test edge cases and error conditions

### Coverage Goals ✅ ACHIEVED
- **SessionManager** - 93% ✅ (target: 100%)
- **Flask routes** - 100% ✅ (target: 90%)
- **WebSocket handlers** - 94% ✅ (target: 90%)
- **Overall** - 94% ✅ (target: 80%+)

## Running the Server ✅ READY

The server is **production-ready** and can be started immediately:

### Development
```bash
# Install dependencies (first time only)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start development server
python run.py
# Server runs at: http://0.0.0.0:5000
# Dashboard URL: http://localhost:5000/dashboard/<session-id>

# Run all tests
pytest -v

# Run tests with coverage
pytest --cov=app --cov-report=html

# Skip slow tests (recommended during development)
pytest -v -m "not slow"
```

### Production
```bash
# Start production server
gunicorn -c gunicorn_config.py run:app

# With Docker
docker-compose up -d

# Deploy to Heroku
git push heroku main
```

## API Contracts

### WebSocket Events (Monitor → Server)

**`request_session_id`**
```python
# Payload: {}
# Response: session_id_assigned event
```

**`setup_data`**
```python
{
    'session_id': str,
    'timestamp': ISO timestamp,
    'setup': {
        'suspension': {...},
        'aerodynamics': {...},
        'brakes': {...}
    }
}
```

**`telemetry_update`**
```python
{
    'session_id': str,
    'telemetry': {
        'timestamp': ISO timestamp,
        'lap': int,
        'position': int,
        'fuel': float,
        'fuel_capacity': float,
        'tire_pressures': {'fl': float, 'fr': float, 'rl': float, 'rr': float},
        'tire_temps': {...},
        'brake_temps': {...},
        'engine_water_temp': float,
        'track_temp': float,
        'ambient_temp': float,
        ...
    }
}
```

See `RACE_DASHBOARD_PLAN.md` lines 1244-1378 for complete API specification.

## WebSocket Events (Server → Dashboard)

**`setup_update`**
- Sent when dashboard joins session (if setup available)
- Sent when server receives setup from monitor
- Payload: Same as `setup_data`

**`telemetry_update`**
- Sent at 2Hz when monitor publishes telemetry
- Broadcast to all dashboards in session room
- Payload: Same as `telemetry_update`

## Important Patterns

### Session URL Format
```
http://server:5000/dashboard/<session-id>

Example:
http://192.168.1.100:5000/dashboard/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Room-Based Broadcasting
```python
from flask_socketio import emit, join_room

# Dashboard joins session room
@socketio.on('join_session')
def handle_join(data):
    session_id = data['session_id']
    join_room(session_id)

# Broadcast to all dashboards in room
@socketio.on('telemetry_update')
def handle_telemetry(data):
    session_id = data['session_id']
    emit('telemetry_update', data, room=session_id)
```

## Bug Tracking Workflow

**When implementing a feature:**
1. Read the feature spec in `bugs/` directory
2. Write tests first (TDD approach)
3. Implement feature to make tests pass
4. Update status in `bugs/README.md` and `PROJECT_STATUS.md`
5. Commit with clear message

**When fixing a bug:**
1. Reproduce the bug
2. Write a failing test
3. Fix the bug (test passes)
4. Update bug file with resolution status (see existing bugs for format)
5. Commit both code and bug documentation

**Bug file format:**
```markdown
## Status: ✅ RESOLVED

**Resolved:** YYYY-MM-DD
**Commit:** <commit-hash>
**Branch:** <branch-name>

**Solution:** Brief description of how the bug was fixed.

---

[Original bug description below...]
```

## Important Files & References

### Key Files
- **`RACE_DASHBOARD_PLAN.md`** - Complete implementation plan (1750 lines)
- **`bugs/README.md`** - Feature index and implementation roadmap
- **`PROJECT_STATUS.md`** - Current implementation progress
- **`swagger-schema.json`** - LMU REST API reference (useful for setup data)
- **`IRACING_FEASIBILITY.md`** - iRacing integration research (future)

### Reference Material (Archived)
- **`_archive/src/lmu_rest_api.py`** - LMU REST API client (reference)
- **`_archive/src/telemetry/`** - Telemetry readers (could be reused by monitor)
- **`_archive/tests/`** - Testing patterns and examples

## Configuration

### Development (`.env`)
```bash
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
HOST=0.0.0.0
PORT=5000
```

### Production
```bash
DEBUG=False
SECRET_KEY=<random-secret-key>
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=https://yourdomain.com
```

## Deployment Options

### Local Network (Simplest)
```bash
# Run on driver's PC
python run.py

# Access via LAN
http://192.168.1.100:5000/dashboard/<session-id>
```

### Cloud (Heroku/Railway/Render)
```bash
# Deploy to cloud
git push heroku main

# Access from anywhere
https://1lap-dashboard.herokuapp.com/dashboard/<session-id>
```

See `bugs/deployment_configuration.md` for detailed deployment guides.

## Code Style & Conventions

- **Docstrings**: Google-style for all functions/classes
- **Type hints**: Use for function signatures
- **Imports**: Group by stdlib, third-party, local
- **Naming**:
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPER_CASE for constants
- **Line length**: ~100 chars when possible

## Troubleshooting

### Tests failing?
1. Check virtual environment is activated
2. Ensure all dependencies installed (`pip install -r requirements.txt requirements-dev.txt`)
3. Read test output carefully
4. Run single test file to isolate issue

### WebSocket not connecting?
1. Check server is running
2. Verify CORS configuration
3. Check browser console for errors
4. Ensure eventlet is installed

### Dashboard shows "Disconnected"?
1. Check monitor is running and connected
2. Verify session ID is correct
3. Check server logs for errors
4. Test WebSocket connection manually

## Next Session Checklist

When continuing development:

1. Pull latest code from git
2. Activate virtual environment
3. Run tests to verify everything works (`pytest -v`)
4. Read `PROJECT_STATUS.md` for current progress
5. Check `bugs/README.md` for next task
6. Review feature spec in `bugs/` before implementing

## Questions to Ask User

Before making significant changes:
- **Adding new dependencies?** → Ask first
- **Changing test behavior?** → Only if tests can't pass after thorough attempts
- **Modifying core architecture?** → Discuss rationale
- **Deployment approach?** → Confirm local vs. cloud requirements

## Success Criteria

**MVP Complete:** ✅ ACHIEVED (2025-11-22)
- ✅ All Phase 1 features implemented (6/6 complete)
- ✅ 94% test coverage (exceeds 80% target)
- ✅ All 62 tests passing
- ✅ Can deploy to local network (python run.py)
- ✅ Dashboard works on mobile devices (responsive design)
- ✅ CI/CD testing via GitHub Actions

**Production Ready when:** (Phase 2 - Optional)
- ⏳ Error handling & reconnection (Phase 2)
- ⏳ Deployment configuration (Phase 2)
- ⏳ User documentation (Phase 2)

---

**Remember**:
- Follow TDD - write tests first, make them fail, then implement
- Reference feature specs in `bugs/` directory
- Update `PROJECT_STATUS.md` as features are completed
- The user values this systematic approach - maintain it throughout
- The archived writer code in `_archive/` is for reference only
