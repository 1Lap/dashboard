# 1Lap Race Dashboard Server

Real-time telemetry dashboard for endurance racing teams. Monitor fuel, tire temperatures, pressures, and car setup from any device during the race.

![Status](https://img.shields.io/badge/status-planning-yellow)
![Phase](https://img.shields.io/badge/phase-ready--for--dev-blue)
![Tests](https://img.shields.io/badge/tests-0%2F60-red)
![Coverage](https://img.shields.io/badge/coverage-0%25-red)

---

## 🏁 Overview

During endurance races, drivers change car settings (tire pressures, fuel strategy, wing angles), but the team cannot see these in real-time. When the team wants to confirm a setting, they must ask the driver, which is distracting.

**Solution:** The 1Lap Dashboard Server receives telemetry from a monitor app (running on the driver's PC with LMU) and broadcasts it to web dashboards accessible by the entire team via secret URLs.

---

## ✨ Features

- 🔴 **Real-time telemetry** - Fuel, tires, brakes, engine temps (2Hz updates)
- 🔧 **Car setup display** - View complete mechanical setup from REST API
- 📱 **Mobile friendly** - Works on phone, tablet, laptop (responsive design)
- 🔗 **Secret URLs** - Share dashboard via unique session link
- 🌐 **Multi-viewer** - Multiple team members view same session simultaneously
- 🔄 **Auto-reconnect** - Resilient to connection drops
- 🚀 **Easy deployment** - Local network or cloud (Heroku/Railway)

---

## 🎯 Status: Planning Phase

**Current Status:** Feature specifications complete, ready for implementation

| Phase | Status | Progress |
|-------|--------|----------|
| Planning | ✅ Complete | 100% |
| Phase 1: MVP | 🔴 Not Started | 0% |
| Phase 2: Polish | 🔴 Not Started | 0% |

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed progress tracking.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LMU (Windows)                        │
│  ┌──────────────┐          ┌─────────────────┐         │
│  │ Shared Mem   │          │   REST API      │         │
│  │ (Telemetry)  │          │ (localhost:6397)│         │
│  └──────┬───────┘          └────────┬────────┘         │
└─────────┼──────────────────────────┼──────────────────┘
          │                          │
          └──────────┬───────────────┘
                     ▼
          ┌──────────────────────┐
          │   monitor (Python)   │  ← Separate repo
          │   - Reads data       │
          │   - Publishes 2Hz    │
          └──────────┬───────────┘
                     │ WebSocket
                     ▼
          ┌──────────────────────┐
          │   server (Flask)     │  ← THIS REPO
          │   - Session mgmt     │
          │   - Broadcast        │
          │   - Serve UI         │
          └──────────┬───────────┘
                     │ WebSocket
                     ▼
          ┌──────────────────────┐
          │   Web Browser        │
          │   - Dashboard UI     │
          │   - Auto-update      │
          └──────────────────────┘
```

---

## 🚀 Quick Start

**Note:** This repo is in planning phase. No code is implemented yet. See `bugs/` directory for feature specifications.

### Installation (Future)

```bash
# Clone repository
git clone https://github.com/1Lap/dashboard.git
cd dashboard

# Install dependencies
pip install -r requirements.txt

# Start server
python run.py
```

### Usage (Future)

1. Start dashboard server: `python run.py`
2. Run monitor (on Windows with LMU): `python monitor.py`
3. Monitor displays dashboard URL:
   ```
   📱 DASHBOARD URL:
      http://192.168.1.100:5000/dashboard/abc-def-ghi
   ```
4. Share URL with team
5. Team opens URL in browser → real-time telemetry!

---

## 📂 Repository Structure

```
dashboard/
├── bugs/                    # Feature specifications (9 detailed specs)
│   ├── README.md           # Feature index & implementation roadmap
│   ├── session_management.md
│   ├── flask_app_structure.md
│   ├── websocket_server.md
│   ├── dashboard_ui_frontend.md
│   └── ...
├── app/                     # Flask application (not implemented yet)
├── static/                  # CSS, JS, images (not implemented yet)
├── templates/               # HTML templates (not implemented yet)
├── tests/                   # Test suite (not implemented yet)
├── RACE_DASHBOARD_PLAN.md  # Complete implementation plan (1750 lines)
├── PROJECT_STATUS.md        # Implementation progress tracker
├── README.md                # This file
└── _archive/                # Archived writer project code (reference)
```

---

## 📋 Implementation Plan

### Week 1: Core Backend
1. **Session Management** - UUID generation, data storage
2. **Flask App Structure** - App factory, routes, configuration
3. **WebSocket Server** - Real-time communication layer
4. **Testing Infrastructure** - pytest setup, fixtures, mocks

### Week 2: Frontend & Polish
5. **Dashboard UI** - HTML/CSS/JS interface with real-time updates
6. **Secret URLs** - Session URL handling (included in #1)
7. **Error Handling** - Auto-reconnect, graceful degradation

### Week 3: Deployment
8. **Deployment Config** - Gunicorn, Docker, cloud guides
9. **Documentation** - README, installation, usage, API reference

See [bugs/README.md](bugs/README.md) for detailed feature specifications.

---

## 🧪 Testing Strategy

**Target:** 80%+ code coverage

### Test Categories
- **Unit Tests** - 32 specified (SessionManager, routes, WebSocket)
- **Integration Tests** - E2E flow, multi-client, reconnection
- **Manual Tests** - Mobile devices, browsers, long sessions

See [bugs/testing_infrastructure.md](bugs/testing_infrastructure.md) for details.

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.11+
- Flask 2.3+ (web framework)
- Flask-SocketIO 5.3+ (WebSocket support)
- eventlet (async mode)
- gunicorn (production)

**Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript (no framework)
- Socket.IO client (CDN)

**Testing:**
- pytest 7.4+
- pytest-cov (coverage)
- pytest-flask (Flask testing)

---

## 📡 API Overview

### WebSocket Events

**Monitor → Server:**
- `request_session_id` - Get unique session ID
- `setup_data` - Send car setup (once per session)
- `telemetry_update` - Send telemetry (2Hz)

**Server → Dashboard:**
- `setup_update` - Broadcast setup to viewers
- `telemetry_update` - Broadcast telemetry (2Hz)

**Dashboard → Server:**
- `join_session` - Join session room to receive updates

See [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) lines 1244-1378 for complete API specification.

---

## 🚢 Deployment Options

### Local Network (Recommended for Testing)
```bash
# Run on driver's PC
python run.py

# Team connects via LAN
http://192.168.1.100:5000/dashboard/<session-id>
```

**Pros:** No cloud costs, low latency, no internet required
**Cons:** Requires LAN access

### Cloud Hosting (Recommended for Remote Teams)
```bash
# Deploy to Heroku/Railway/Render
git push heroku main

# Access from anywhere
https://dashboard.1lap.io/<session-id>
```

**Pros:** Accessible from anywhere, no firewall issues
**Cons:** Requires internet, slight latency increase

See [bugs/deployment_configuration.md](bugs/deployment_configuration.md) for detailed guides.

---

## 📚 Documentation

### For Developers
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Implementation progress
- [bugs/README.md](bugs/README.md) - Feature specifications index
- [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) - Complete plan
- [.claude/CLAUDE.md](.claude/CLAUDE.md) - Development guidelines

### For Users (Future)
- Installation guide - Not yet written
- Usage guide - Not yet written
- Troubleshooting - Not yet written
- API reference - Not yet written

---

## 🤝 Contributing

This project follows **Test-Driven Development (TDD)**:

1. Read feature spec in `bugs/` directory
2. Write failing tests first
3. Implement feature to make tests pass
4. Update `PROJECT_STATUS.md` with progress
5. Commit with clear message

See [.claude/CLAUDE.md](.claude/CLAUDE.md) for detailed development guidelines.

---

## 🔗 Related Projects

| Project | Purpose | Status |
|---------|---------|--------|
| **dashboard** (this repo) | Web server for real-time telemetry display | Planning |
| **monitor** | Data collector (publishes to dashboard) | Planned |
| **writer** | CSV telemetry logger | Complete (archived in `_archive/`) |

---

## 📊 Current Progress

**Last Updated:** 2025-11-22

| Metric | Value |
|--------|-------|
| Features Specified | 9/9 (100%) |
| Features Implemented | 0/9 (0%) |
| Tests Written | 0/60+ (0%) |
| Code Coverage | 0% |
| Documentation | Planning docs only |

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed tracking.

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/1Lap/dashboard/issues)
- **Documentation:** See `bugs/` directory for specs
- **Reference:** LMU REST API schema in `swagger-schema.json`

---

## 🎯 Next Steps

1. ✅ Feature specifications complete (9 files in `bugs/`)
2. 🔜 Update `requirements.txt` with Flask dependencies
3. 🔜 Create directory structure (`app/`, `static/`, `templates/`, `tests/`)
4. 🔜 Implement SessionManager (Week 1)
5. 🔜 Build Flask app with WebSocket support (Week 1)
6. 🔜 Create dashboard UI (Week 2)
7. 🔜 Deploy to local network (Week 3)

**Ready to start implementation!** 🚀

See [bugs/README.md](bugs/README.md) for detailed implementation roadmap.

---

Built with ❤️ for endurance racing teams
