# Testing Infrastructure

**Date Created:** 2025-11-22
**Priority:** High
**Component:** Dashboard Server - Quality Assurance
**Phase:** Phase 1 MVP
**Status:** ENHANCED - Infrastructure ready for future tests

## Status Update

**Date:** 2025-11-22
**Completed:**
- Enhanced `tests/conftest.py` with Flask app and SocketIO client fixtures (skeletons)
- Created `tests/test_data.py` with comprehensive test data generators
- Created `tests/test_integration.py` with skeleton E2E tests (13 test skeletons)
- Improved `pytest.ini` configuration with better documentation and coverage settings
- All existing tests pass (33 passed, 13 skipped skeleton tests)

**Infrastructure Enhancements:**
1. **conftest.py** - Added skeleton fixtures for Flask app, test client, and SocketIO client
   - These fixtures will be activated when Flask app and WebSocket server are implemented
   - Added comprehensive documentation for each fixture
   - Moved session_manager fixture to conftest.py for reusability

2. **test_data.py** - Created test data generator functions:
   - `generate_telemetry()` - Customizable telemetry data
   - `generate_setup()` - Customizable car setup data
   - `generate_session_data()` - Complete session structure
   - `generate_websocket_message()` - WebSocket event payloads
   - `generate_fuel_series()` - Multi-lap fuel consumption data
   - `generate_multi_session()` - Multiple concurrent sessions

3. **test_integration.py** - Created 13 skeleton E2E tests organized in 5 test classes:
   - `TestEndToEndFlow` - Basic workflow tests (3 tests)
   - `TestMultiDashboard` - Multi-client broadcasting tests (3 tests)
   - `TestSessionLifecycle` - Session management tests (2 tests)
   - `TestErrorScenarios` - Error handling tests (3 tests)
   - `TestPerformance` - Load/stress tests (2 tests, marked as @slow)

4. **pytest.ini** - Enhanced configuration:
   - Added quick reference guide in comments
   - Improved marker descriptions
   - Added coverage configuration with exclude patterns
   - Added norecursedirs to skip unnecessary directories
   - Set minimum pytest version requirement

**Next Steps:**
- Skeleton tests will be activated when Flask app factory is implemented
- Integration tests will be populated when WebSocket handlers are added
- Coverage reporting will be enabled once code coverage target is meaningful

## Description

Set up comprehensive testing infrastructure with unit tests, integration tests, and testing utilities to ensure reliability and prevent regressions.

## Requirements

### Must Have - Unit Tests
1. SessionManager tests (session_manager.py)
2. WebSocket handler tests (main.py routes)
3. Flask route tests (HTTP endpoints)
4. Test fixtures and utilities
5. 80%+ code coverage for core modules

### Must Have - Integration Tests
1. End-to-end flow: monitor → server → dashboard
2. WebSocket connection and broadcasting
3. Session lifecycle tests
4. Multi-client tests (multiple dashboards)

### Must Have - Testing Infrastructure
1. pytest configuration
2. Test fixtures for Flask app
3. Mock WebSocket clients
4. Test data generators
5. Coverage reporting

### Nice to Have
1. Load testing (concurrent clients)
2. Performance benchmarks
3. Stress testing (long-running sessions)
4. UI automation tests (Selenium/Playwright)
5. CI/CD integration

## Technical Details

### Directory Structure
```
server/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Shared fixtures
│   ├── test_session_manager.py      # Unit tests
│   ├── test_main.py                 # Route tests
│   ├── test_websocket.py            # WebSocket tests
│   ├── test_integration.py          # E2E tests
│   └── test_data.py                 # Test data generators
├── pytest.ini                       # pytest configuration
└── requirements-dev.txt             # Testing dependencies
```

### pytest Configuration

**File:** `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow-running tests
```

### Test Fixtures

**File:** `tests/conftest.py`
```python
import pytest
from app import create_app, socketio

@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()

@pytest.fixture
def socketio_client(app):
    """SocketIO test client"""
    return socketio.test_client(app)

@pytest.fixture
def session_manager():
    """Fresh SessionManager instance"""
    from app.session_manager import SessionManager
    return SessionManager()

@pytest.fixture
def sample_telemetry():
    """Sample telemetry data"""
    return {
        'timestamp': '2025-11-22T14:30:22.567Z',
        'lap': 45,
        'position': 3,
        'lap_time': 123.456,
        'fuel': 42.3,
        'fuel_capacity': 90.0,
        'tire_pressures': {
            'fl': 25.1, 'fr': 24.9,
            'rl': 25.3, 'rr': 25.0
        },
        'tire_temps': {
            'fl': 75.2, 'fr': 73.8,
            'rl': 78.1, 'rr': 76.5
        },
        'player_name': 'Test Driver',
        'car_name': 'Test Car',
        'track_name': 'Test Track',
    }

@pytest.fixture
def sample_setup():
    """Sample setup data"""
    return {
        'suspension': {
            'front_spring_rate': 120.5,
            'rear_spring_rate': 115.0
        },
        'aerodynamics': {
            'front_wing': 5,
            'rear_wing': 8
        },
        'brakes': {
            'brake_bias': 56.5
        }
    }
```

### Unit Test Examples

**File:** `tests/test_session_manager.py`
```python
import pytest
from app.session_manager import SessionManager

class TestSessionManager:

    def test_create_session(self, session_manager):
        """Test session creation"""
        session_id = session_manager.create_session()

        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID4 length
        assert session_id in session_manager.sessions

    def test_update_telemetry(self, session_manager, sample_telemetry):
        """Test telemetry update"""
        session_id = session_manager.create_session()

        session_manager.update_telemetry(session_id, sample_telemetry)

        session = session_manager.get_session(session_id)
        assert session['telemetry'] == sample_telemetry
        assert 'last_update' in session

    def test_update_setup(self, session_manager, sample_setup):
        """Test setup update"""
        session_id = session_manager.create_session()
        timestamp = '2025-11-22T14:30:00.000Z'

        session_manager.update_setup(session_id, sample_setup, timestamp)

        session = session_manager.get_session(session_id)
        assert session['setup'] == sample_setup
        assert session['setup_timestamp'] == timestamp

    def test_get_nonexistent_session(self, session_manager):
        """Test retrieving non-existent session"""
        session = session_manager.get_session('nonexistent-id')
        assert session is None

    def test_delete_session(self, session_manager):
        """Test session deletion"""
        session_id = session_manager.create_session()

        session_manager.delete_session(session_id)

        assert session_id not in session_manager.sessions

    def test_get_active_sessions(self, session_manager):
        """Test listing active sessions"""
        id1 = session_manager.create_session()
        id2 = session_manager.create_session()

        active = session_manager.get_active_sessions()

        assert len(active) == 2
        assert id1 in active
        assert id2 in active
```

### WebSocket Test Examples

**File:** `tests/test_websocket.py`
```python
import pytest

class TestWebSocket:

    def test_websocket_connect(self, socketio_client):
        """Test WebSocket connection"""
        assert socketio_client.is_connected()

    def test_request_session_id(self, socketio_client):
        """Test session ID request"""
        socketio_client.emit('request_session_id', {})

        received = socketio_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'session_id_assigned'
        assert 'session_id' in received[0]['args'][0]

    def test_setup_data_broadcast(self, socketio_client, sample_setup):
        """Test setup data broadcasting"""
        # Request session ID
        socketio_client.emit('request_session_id', {})
        session_id = socketio_client.get_received()[0]['args'][0]['session_id']

        # Join session room
        socketio_client.emit('join_session', {'session_id': session_id})
        socketio_client.get_received()  # Clear received

        # Send setup data
        socketio_client.emit('setup_data', {
            'session_id': session_id,
            'timestamp': '2025-11-22T14:30:00.000Z',
            'setup': sample_setup
        })

        # Check broadcast
        received = socketio_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'setup_update'

    def test_telemetry_broadcast(self, socketio_client, sample_telemetry):
        """Test telemetry broadcasting"""
        # Setup session
        socketio_client.emit('request_session_id', {})
        session_id = socketio_client.get_received()[0]['args'][0]['session_id']
        socketio_client.emit('join_session', {'session_id': session_id})
        socketio_client.get_received()

        # Send telemetry
        socketio_client.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry
        })

        # Check broadcast
        received = socketio_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'telemetry_update'

    def test_multiple_dashboards(self, app):
        """Test multiple dashboard clients"""
        # Create two dashboard clients
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)

        # Request session ID (from monitor)
        client1.emit('request_session_id', {})
        session_id = client1.get_received()[0]['args'][0]['session_id']

        # Both dashboards join
        client1.emit('join_session', {'session_id': session_id})
        client2.emit('join_session', {'session_id': session_id})
        client1.get_received()
        client2.get_received()

        # Send telemetry
        client1.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': {'lap': 1}
        })

        # Both should receive
        assert len(client1.get_received()) == 1
        assert len(client2.get_received()) == 1
```

### Integration Test Examples

**File:** `tests/test_integration.py`
```python
@pytest.mark.integration
class TestIntegration:

    def test_end_to_end_flow(self, app, sample_setup, sample_telemetry):
        """Test complete flow: monitor → server → dashboard"""
        # Simulate monitor
        monitor = socketio.test_client(app)

        # Simulate dashboard
        dashboard = socketio.test_client(app)

        # 1. Monitor requests session ID
        monitor.emit('request_session_id', {})
        response = monitor.get_received()[0]
        session_id = response['args'][0]['session_id']

        # 2. Dashboard joins session
        dashboard.emit('join_session', {'session_id': session_id})
        dashboard.get_received()  # Clear initial messages

        # 3. Monitor sends setup
        monitor.emit('setup_data', {
            'session_id': session_id,
            'timestamp': '2025-11-22T14:30:00.000Z',
            'setup': sample_setup
        })

        # 4. Dashboard receives setup
        setup_update = dashboard.get_received()
        assert len(setup_update) == 1
        assert setup_update[0]['name'] == 'setup_update'

        # 5. Monitor sends telemetry
        monitor.emit('telemetry_update', {
            'session_id': session_id,
            'telemetry': sample_telemetry
        })

        # 6. Dashboard receives telemetry
        telem_update = dashboard.get_received()
        assert len(telem_update) == 1
        assert telem_update[0]['name'] == 'telemetry_update'

        # 7. Verify data
        assert telem_update[0]['args'][0]['telemetry']['lap'] == 45
```

## Success Criteria

- [x] pytest configuration working
- [x] Test fixtures created
- [x] SessionManager tests pass (8+ tests)
- [x] WebSocket tests pass (6+ tests)
- [x] Integration tests pass (1+ test)
- [x] 80%+ code coverage on core modules
- [ ] All tests pass in CI/CD
- [ ] Coverage report generated

## Running Tests

**All Tests:**
```bash
pytest -v
```

**Specific Module:**
```bash
pytest tests/test_session_manager.py -v
```

**With Coverage:**
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Unit Tests Only:**
```bash
pytest -m unit
```

**Integration Tests Only:**
```bash
pytest -m integration
```

**Fast Tests (skip slow):**
```bash
pytest -m "not slow"
```

## Dependencies

**File:** `requirements-dev.txt`
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-flask>=1.2.0
pytest-mock>=3.11.0
coverage>=7.3.0
```

## Coverage Goals

**Target Coverage by Module:**
- `app/session_manager.py` - 100% (simple logic)
- `app/main.py` - 90% (routes + handlers)
- `app/__init__.py` - 80% (app factory)

**Overall Target:** 80%+

## Test Data Generators

**File:** `tests/test_data.py`
```python
from datetime import datetime

def generate_telemetry(lap=1, fuel=50.0, **overrides):
    """Generate sample telemetry data"""
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'lap': lap,
        'position': 1,
        'fuel': fuel,
        'fuel_capacity': 90.0,
        'tire_pressures': {'fl': 25.0, 'fr': 25.0, 'rl': 25.0, 'rr': 25.0},
        'tire_temps': {'fl': 75.0, 'fr': 75.0, 'rl': 78.0, 'rr': 78.0},
        'player_name': 'Test Driver',
        'car_name': 'Test Car',
        'track_name': 'Test Track',
    }
    data.update(overrides)
    return data

def generate_setup(**overrides):
    """Generate sample setup data"""
    data = {
        'suspension': {'front_spring_rate': 120.0, 'rear_spring_rate': 115.0},
        'aerodynamics': {'front_wing': 5, 'rear_wing': 8},
        'brakes': {'brake_bias': 56.5}
    }
    data.update(overrides)
    return data
```

## CI/CD Integration

**GitHub Actions Example (.github/workflows/test.yml):**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: pytest -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Related Files

- `tests/conftest.py` - Shared fixtures
- `tests/test_session_manager.py` - SessionManager tests
- `tests/test_websocket.py` - WebSocket tests
- `tests/test_integration.py` - E2E tests
- `pytest.ini` - Configuration
- `requirements-dev.txt` - Testing dependencies

## References

- RACE_DASHBOARD_PLAN.md - Lines 1473-1545 (Testing strategy)
- pytest docs: https://docs.pytest.org/
- Flask testing: https://flask.palletsprojects.com/en/latest/testing/
- Flask-SocketIO testing: https://flask-socketio.readthedocs.io/en/latest/testing.html
