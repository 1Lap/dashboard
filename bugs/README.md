# Dashboard MVP - Feature & Bug Tracker

This directory contains feature specifications and bug reports for the **1Lap Race Dashboard** server component.

## Overview

The dashboard is a Flask-based WebSocket server that receives telemetry from the monitor (running on Windows with LMU) and broadcasts it to web-based dashboards accessible by team members via secret URLs.

## Phase 1 MVP Features (High Priority)

These features are required for the initial release:

### Core Server Components

1. **[Session Management](session_management.md)** ⭐ HIGH PRIORITY
   - UUID generation for session IDs
   - Session data storage (setup + telemetry)
   - Multi-session support
   - **Status:** Not started
   - **Tests:** `test_session_manager.py`

2. **[Flask App Structure](flask_app_structure.md)** ⭐ HIGH PRIORITY
   - Flask app factory pattern
   - HTTP routes (/, /dashboard/<id>)
   - Configuration management
   - Static file serving
   - **Status:** Not started
   - **Tests:** `test_main.py`

3. **[WebSocket Server](websocket_server.md)** ⭐ HIGH PRIORITY
   - Monitor → Server communication
   - Dashboard → Server communication
   - Room-based broadcasting
   - Event handlers (setup, telemetry, join)
   - **Status:** Not started
   - **Tests:** `test_websocket.py`

### Frontend

4. **[Dashboard UI Frontend](dashboard_ui_frontend.md)** ⭐ HIGH PRIORITY ✅ COMPLETED
   - Single-page web app (HTML/CSS/JS)
   - Real-time telemetry display
   - Setup data display
   - Mobile responsive design
   - Connection status indicator
   - **Status:** ✅ Complete (2025-11-22)
   - **Tests:** Manual testing checklist - PASSED

### Session URLs

5. **[Secret URL Generation](secret_url_generation.md)** ⭐ HIGH PRIORITY
   - UUID-based session URLs
   - URL persistence throughout race
   - Multi-viewer support
   - URL display on monitor
   - **Status:** Not started
   - **Tests:** Unit tests in `test_session_manager.py`

### Quality Assurance

6. **[Testing Infrastructure](testing_infrastructure.md)** ⭐ HIGH PRIORITY
   - pytest setup
   - Unit tests (SessionManager, routes)
   - Integration tests (E2E flow)
   - WebSocket tests
   - Test fixtures and data generators
   - **Status:** Not started
   - **Coverage Goal:** 80%+

## Phase 2 Polish Features (Medium Priority)

These features improve reliability and user experience:

7. **[Error Handling & Reconnection](error_handling_reconnection.md)** 🔶 MEDIUM PRIORITY
   - Monitor auto-reconnect with backoff
   - Dashboard auto-reconnect
   - Server error handling
   - Stale data warnings
   - **Status:** Not started
   - **Tests:** `test_reconnection.py`

8. **[Deployment Configuration](deployment_configuration.md)** 🔶 MEDIUM PRIORITY
   - Local network setup
   - Gunicorn configuration
   - Docker containerization
   - Cloud deployment (Heroku, Railway)
   - Environment variables
   - **Status:** Not started

9. **[Documentation & README](documentation_and_readme.md)** 🔶 MEDIUM PRIORITY
   - README.md with quick start
   - Installation guide
   - Usage guide
   - API reference
   - Troubleshooting guide
   - **Status:** Not started

## Feature Status Summary

| Feature | Priority | Status | Tests | Dependencies |
|---------|----------|--------|-------|--------------|
| Session Management | ⭐ High | Not Started | 0/8 | None |
| Flask App Structure | ⭐ High | Not Started | 0/7 | Session Mgmt |
| WebSocket Server | ⭐ High | Not Started | 0/9 | Session Mgmt, Flask |
| Dashboard UI | ⭐ High | ✅ Complete | ✅ Passed | WebSocket Server |
| Secret URLs | ⭐ High | Not Started | 0/4 | Session Mgmt |
| Testing Infrastructure | ⭐ High | Not Started | Setup | All features |
| Error Handling | 🔶 Medium | Not Started | 0/8 | WebSocket Server |
| Deployment | 🔶 Medium | Not Started | Manual | All Phase 1 |
| Documentation | 🔶 Medium | Not Started | N/A | All features |

## Implementation Order

**Recommended sequence:**

### Week 1: Core Backend
1. **Session Management** (Day 1) - Foundation for everything
2. **Flask App Structure** (Day 1-2) - Server setup
3. **WebSocket Server** (Day 2-3) - Communication layer
4. **Testing Infrastructure** (Day 3) - Validate as you build

### Week 2: Frontend & Polish
5. **Dashboard UI** (Day 4-5) - User interface
6. **Secret URLs** (Day 5) - URL handling (mostly done in #1)
7. **Error Handling** (Day 6) - Reliability
8. **Documentation** (Day 7) - User guides

### Week 3: Deployment
9. **Deployment Configuration** (Day 8-9) - Local + cloud
10. **End-to-end Testing** (Day 9-10) - Full system validation

## Testing Checklist

### Unit Tests
- [ ] SessionManager (8 tests)
- [ ] Flask routes (7 tests)
- [ ] WebSocket handlers (9 tests)
- [ ] Error handling (8 tests)

### Integration Tests
- [ ] End-to-end flow (monitor → server → dashboard)
- [ ] Multi-client (multiple dashboards)
- [ ] Reconnection scenarios

### Manual Tests
- [ ] Local network access
- [ ] Mobile device rendering
- [ ] Browser compatibility (Chrome, Firefox, Safari)
- [ ] Connection loss recovery
- [ ] Long-running session (>1 hour)

## Success Criteria for MVP

**Phase 1 Complete when:**
- ✅ Monitor connects and receives session ID
- ✅ Monitor publishes setup data (once)
- ✅ Monitor publishes telemetry (2Hz)
- ✅ Dashboard loads at secret URL
- ✅ Dashboard receives and displays telemetry
- ✅ Multiple dashboards can view same session
- ✅ UI is mobile responsive
- ✅ 80%+ test coverage on core modules
- ✅ All unit tests pass
- ✅ Integration tests pass

**Phase 2 Complete when:**
- ✅ Error handling graceful (no crashes)
- ✅ Auto-reconnection works
- ✅ Documentation complete
- ✅ Can deploy to local network
- ✅ Can deploy to cloud (Heroku/Railway)
- ✅ Manual testing checklist complete

## Technology Stack

**Backend:**
- Python 3.11+
- Flask 2.3+
- Flask-SocketIO 5.3+
- python-socketio 5.9+
- eventlet (async mode)

**Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript (no framework)
- Socket.IO client (CDN)

**Testing:**
- pytest 7.4+
- pytest-cov 4.1+
- pytest-flask 1.2+

**Deployment:**
- Gunicorn (production)
- Docker (optional)
- Heroku/Railway (cloud)

## Related Documentation

- [RACE_DASHBOARD_PLAN.md](../RACE_DASHBOARD_PLAN.md) - Complete implementation plan
- Monitor repository - Data collector (separate repo)

## Contributing

When working on a feature:

1. **Read the feature spec** - Understand requirements
2. **Follow TDD** - Write tests first (if applicable)
3. **Implement feature** - Make tests pass
4. **Update status** - Mark feature as complete
5. **Document** - Update README/docs

When fixing a bug:

1. **Reproduce** - Verify bug exists
2. **Write test** - Test should fail
3. **Fix** - Make test pass
4. **Update bug file** - Add resolution status (see existing bugs for format)

## Questions?

- See [RACE_DASHBOARD_PLAN.md](../RACE_DASHBOARD_PLAN.md) for architecture details
- Check individual feature files for technical specs
- Review API contracts in WebSocket Server spec

---

**Last Updated:** 2025-11-22
**Status:** Planning Phase - Ready for implementation
