# Archived GitHub Actions Workflows

These workflows are from the **writer project** (CSV telemetry logger) and are preserved here for reference only.

## Workflows

### `test.yml` - Writer Project Tests
**Purpose:** Run pytest on writer source code
- Tested `src/` directory (telemetry reader, CSV formatter, etc.)
- Ran on Ubuntu and Windows
- Required `requirements-windows.txt` for Windows-specific deps
- Achieved 100% coverage on writer modules

**Not applicable to dashboard** because:
- Dashboard has different source structure (`app/` not `src/`)
- No Windows-specific dependencies needed
- Different test requirements (Flask/WebSocket vs telemetry)

### `build-release.yml` - Writer PyInstaller Builds
**Purpose:** Build Windows .exe and installer for writer desktop app
- Built single-file executable with PyInstaller
- Created Inno Setup installer
- Posted build artifacts to PR comments
- Created GitHub releases on version tags

**Not applicable to dashboard** because:
- Dashboard is a web service (Flask), not a desktop app
- No need for .exe builds (runs as Python service)
- Deployment is to web servers (Heroku/Railway), not Windows installs
- Dashboard runs continuously on server, not as background tray app

## Why Archived?

The dashboard is a fundamentally different type of application:

| Aspect | Writer (Archived) | Dashboard (New) |
|--------|-------------------|-----------------|
| **Type** | Desktop background app | Web service |
| **Distribution** | .exe installer | Cloud deployment |
| **Platform** | Windows only | Platform-agnostic |
| **Interface** | System tray UI | Web browser UI |
| **Testing** | Desktop app tests | Web service tests |
| **Deployment** | User installs locally | Deploy to server |

## Future Dashboard Workflows

The dashboard will eventually have workflows for:
- **Testing:** pytest with Flask-SocketIO mocking
- **Deployment:** Deploy to Heroku/Railway/Docker
- **Linting:** Code quality checks
- **Security:** Dependency scanning

See `/.github/workflows/README.md` for planned dashboard workflows.

---

**Last Updated:** 2025-11-22
**Archive Date:** 2025-11-22
**Reason:** Repository transitioned from writer to dashboard project
