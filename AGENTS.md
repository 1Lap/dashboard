1Lap Dashboard Server — AGENTS Guide

Purpose
- Flask + Flask‑SocketIO server that issues session IDs, receives telemetry/setup from the monitor, and broadcasts updates to browser dashboards.

Repo Relationships
- monitor: publishes telemetry/setup to this server (WebSocket)
- dashboard (this repo): server + web UI (templates/static)

Quick Start
- Install deps: `pip install -r requirements.txt -r requirements-dev.txt`
- Run dev server: `python run.py` (http://0.0.0.0:5000)
- Run tests: `pytest -v` or with coverage `pytest --cov=app --cov-report=html`
- Start prod: `gunicorn -c gunicorn_config.py run:app` or `docker-compose up -d`

Key Components
- `app/__init__.py`: Flask app factory and SocketIO setup
- `app/main.py`: HTTP routes + WebSocket handlers
- `app/session_manager.py`: session IDs, rooming, data storage helpers
- `templates/dashboard.html`: dashboard UI
- `static/js/dashboard.js`, `static/css/dashboard.css`: front‑end behavior/styles
- `config.py`: configuration

WebSocket Contract
- Monitor → Server:
  - `request_session_id` → Server emits `session_id_assigned`
  - `setup_data` { session_id, timestamp, setup: {...} }
  - `telemetry_update` { session_id, telemetry: {...} }
- Server → Dashboard:
  - `setup_update` (on join + when new setup arrives)
  - `telemetry_update` (broadcast ~2Hz)
- Dashboard → Server:
  - `join_session` { session_id } → server joins room

Routes
- `/` home/status; `/dashboard/<session_id>` serves dashboard UI

Development Workflow (TDD)
- Write failing tests for new behavior before implementing.
- Maintain high coverage on core modules (target ≥80%).
- Keep WebSocket handlers small and covered by unit + integration tests.
- Update `PROJECT_STATUS.md` and relevant `bugs/*.md` when completing features.

Testing
- Unit: `pytest -m unit`; Integration: `pytest -m integration`; All: `pytest -v`
- Coverage: `pytest --cov=app --cov-report=html`
- Use fixtures in `tests/conftest.py`; mock SocketIO clients in tests.

Common Tasks
- Add/adjust a field in telemetry:
  1) Update handler validation/schema usage; 2) ensure broadcasting integrity; 3) adapt UI bindings; 4) add tests.
- Enhance reconnection/error handling:
  1) Harden SocketIO handlers; 2) add tests for disconnect/room rejoin; 3) verify idempotency.
- UI tweak:
  1) Update `templates/dashboard.html` + `static` assets; 2) keep JS minimal; 3) manual check in browser; 4) add assertions in integration tests if applicable.

Guardrails
- Preserve room‑based broadcasting per `session_id` to isolate sessions.
- Keep secrets/keys out of code; use env/config.
- Avoid over‑coupling UI and server events; keep payload contracts stable.
- Ask before adding heavy/new dependencies or changing core event names.

Deployment
- Local LAN: `python run.py` and access `http://<host>:5000/dashboard/<session-id>`
- Production: `gunicorn -c gunicorn_config.py run:app`, or containerize via `docker-compose`.

Status & Next Steps
- MVP complete with high coverage and passing tests.
- Phase 2: reconnection robustness, deployment docs, polish.

References
- `.claude/CLAUDE.md`, `RACE_DASHBOARD_PLAN.md`, `bugs/README.md`, `PROJECT_STATUS.md`, `swagger-schema.json`.

