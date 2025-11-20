# Feature Requests: Phase 5 User Experience Enhancements

**Status**: Not Yet Implemented (Phase 5 pending)
**Priority**: Medium (Nice to have, not critical)
**Category**: User Interface & User Experience

---

## Requested Features

### 1. Auto-Update from GitHub Repository
**Status**: Not Implemented
**Description**: App should check for updates and update itself automatically from the GitHub repo.
**Related Phase**: Phase 5 (System Tray UI & User Controls)

### 2. System Tray Integration
**Status**: Not Implemented ⚠️
**Description**: App should run in the system tray (Windows) or menu bar (macOS) instead of as a command-line application.
**Related Phase**: Phase 5 (System Tray UI & User Controls)
**Note**: `pystray` is already in requirements.txt but not yet implemented

### 3. Configurable Output Directory
**Status**: Partially Implemented ✅
**Description**: Write telemetry into `~/Documents/eztel/my_laps/` folder with user configuration.
**Current Implementation**:
- FileManager supports custom output directories via config
- Default is `./telemetry_output`
- Can be changed in code but no UI for configuration yet
**Missing**: GUI settings menu to change output path

### 4. Settings/Configuration Menu
**Status**: Not Implemented
**Description**: UI menu to configure:
- Output directory path (e.g., `~/Documents/eztel/`)
- Other settings (auto-start, notifications, etc.)
**Related Phase**: Phase 5 (System Tray UI & User Controls)

---

## Implementation Notes

These features are all part of **Phase 5: System Tray UI & User Controls**, which is currently **not implemented**. The core telemetry logging functionality (Phases 1-4, 6) is complete and working. Phase 5 would add the user-friendly UI layer on top of the existing command-line application.

**Current Status**: Application runs as `example_app.py` command-line tool
**Future Status**: Application would run as background service with system tray UI
