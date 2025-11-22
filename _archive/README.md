# Archive - Writer Project Code

This directory contains code and documentation from the **1Lap Telemetry Writer** project (CSV telemetry logger). This code was the original basis for this repository but is not part of the **Dashboard Server** implementation.

## Why This Code is Archived

The dashboard repository was initially created from the writer project, but the dashboard is a completely different component:

- **Writer Project** - Background service that reads LMU telemetry and writes CSV files
- **Dashboard Project** - Flask web server that displays real-time telemetry to team members

These archived files are kept as reference material but are not active in the dashboard codebase.

## What's Archived

### Source Code
- `src/` - All writer source modules
  - `csv_formatter.py` - CSV output formatting
  - `file_manager.py` - File saving and management
  - `session_manager.py` - Writer's session tracking (different from dashboard's)
  - `telemetry_loop.py` - Polling loop for CSV capture
  - `tray_ui.py` - System tray application
  - `update_*.py` - Auto-update system
  - `settings_ui.py` - Settings dialog
  - `telemetry/` - Telemetry readers (mock + real)
  - And more...

### Test Suite
- `tests/` - Complete test suite for writer project (175 tests)

### Applications
- `example_app.py` - Writer example application
- `tray_app.py` - System tray entry point
- `updater.py` - Auto-updater script
- `debug_dump_all_fields.py` - Debug utility
- `test_lmu.py`, `test_lmu_rest_api.py` - Manual test scripts

### Build & Distribution
- `installer/` - Inno Setup installer configuration
- `build.bat` - PyInstaller build script
- `build_installer.bat` - Installer build script
- `pytest.ini` - Test configuration

### Documentation
- `AUTO_UPDATE_IMPLEMENTATION_PLAN.md` - Auto-update design
- `CHANGELOG.md` - Writer version history
- `IMPLEMENTATION_GUIDE.md` - Writer implementation guide
- `MVP_LOGGING_PLAN.md` - CSV format specifications
- `TECHNICAL_SPEC.md` - Writer technical specifications
- `TELEMETRY_LOGGER_PLAN.md` - Writer project plan
- `USER_GUIDE.md` - Writer user guide
- `WINDOWS_BUILD_INSTRUCTIONS.md` - Build instructions
- `WINDOWS_SETUP.md` - Windows setup guide
- `RELEASE_NOTES_v*.md` - Version release notes
- `PR_DESCRIPTION.md`, `PR_SUMMARY.md` - Writer PR documentation
- `telemetry_format_analysis.md` - CSV format analysis
- `example.csv` - Example output file
- `LMU_Telemetry_Logger.spec` - PyInstaller spec

### Sample Data
- `lapdata_examples/` - Example lap data files
- `test_script_output.log` - Test output logs

## Useful Reference Material

Even though this code isn't active, it contains useful patterns and components:

### Reusable Components (if needed)
- `src/telemetry/` - Telemetry readers (could be reused by monitor project)
- `src/lmu_rest_api.py` - LMU REST API client (useful reference)
- `src/process_monitor.py` - Process detection (could be reused)
- `src/mvp_format.py` - Data normalization patterns

### Testing Patterns
- Test organization and fixtures
- Mocking strategies for time-dependent code
- Integration testing examples

### Deployment Knowledge
- Windows installer setup
- PyInstaller configuration
- Auto-update implementation

## Related Projects

**Active Projects:**
- **Dashboard Server** (this repo) - Web dashboard for real-time telemetry
- **Monitor** (separate repo) - Data collector that publishes to dashboard server
- **Writer** (separate repo) - Original CSV telemetry logger

## Archive Date

**Archived:** 2025-11-22
**Reason:** Repository repurposed for Dashboard Server implementation
**Status:** Preserved for reference, no longer maintained in this repo

---

For the active dashboard server implementation, see the root README.md and `bugs/` directory.
