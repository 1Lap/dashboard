# GitHub Actions Workflows

## Status: To Be Implemented

This directory will contain CI/CD workflows for the dashboard server once implementation begins.

## Archived Workflows

The original workflows from the **writer project** have been archived to:
- `_archive/.github/workflows/test.yml` - Writer project tests
- `_archive/.github/workflows/build-release.yml` - Writer PyInstaller builds

These are preserved as reference but are not applicable to the dashboard server.

## Planned Workflows

### Phase 1: Testing (Week 1-2)
**`test.yml`** - Run pytest on push/PR
```yaml
- Install Flask/SocketIO dependencies
- Run pytest with coverage
- Target: 80%+ coverage
- Test on: ubuntu-latest, python 3.11+
```

### Phase 2: Deployment (Week 3+)
**`deploy-heroku.yml`** - Deploy to Heroku (optional)
```yaml
- Triggered on: push to main
- Deploy Flask app to Heroku
- Run health check
```

**`docker-build.yml`** - Build Docker image (optional)
```yaml
- Build dashboard Docker image
- Push to Docker Hub/GitHub Container Registry
- Tag with version
```

## Why Archived?

The writer project workflows:
- Built Windows .exe with PyInstaller (dashboard is a web service)
- Ran tests on `src/` code that no longer exists (moved to `_archive/`)
- Installed Windows dependencies not needed for Flask server
- Created installers for desktop app (dashboard deploys to server)

The dashboard will need different workflows focused on:
- Web service testing (pytest with Flask-SocketIO)
- Cloud deployment (Heroku, Railway, Docker)
- API contract validation (WebSocket events)

## Timeline

- **Now (Planning Phase):** No workflows needed
- **Week 1-2 (MVP Implementation):** Add `test.yml` when tests are written
- **Week 3+ (Deployment):** Add deployment workflows as needed

---

**Last Updated:** 2025-11-22
**Status:** Workflows archived, awaiting dashboard implementation
