# Feature Requests: Phase 5 User Experience Enhancements

**Status**: Not Yet Implemented (Phase 5 pending)
**Priority**: Medium (Nice to have, not critical)
**Category**: User Interface & User Experience

---

## Overview

This file originally contained several feature requests that have now been split into independent, detailed feature specifications. Each feature can be implemented independently.

---

## Split Features

These features have been separated into individual files for better tracking and implementation:

### 1. System Tray Integration
**File**: `feature_system_tray.md`
**Status**: Not Implemented
**Description**: Run app in system tray (Windows) or menu bar (macOS) with basic controls
**Estimated Effort**: 2-3 days
**Original Request**: "it'd be cool if it ran in the system tray"

### 2. Settings/Configuration UI
**File**: `feature_settings_ui.md`
**Status**: Not Implemented
**Description**: GUI dialog for configuring output directory and other settings
**Estimated Effort**: 2-3 days
**Original Request**: "a little config menu where we could specify ~/Documents/eztel/ as the path to write to"

**Note**: Output directory configuration is already implemented in the backend (`FileManager` class), but there's no GUI for it yet.

### 3. Auto-Update from GitHub
**File**: `feature_auto_update.md`
**Status**: Not Implemented
**Description**: Automatic update checking and installation from GitHub releases
**Estimated Effort**: 3-5 days
**Original Request**: "the app looked for updates and updated itself, from the github repo"

---

## Feature Dependencies

These features are **independent** and can be implemented in any order:

- **System Tray** works standalone (no dependencies)
- **Settings UI** works standalone (can be opened from command-line or system tray)
- **Auto-Update** works standalone (can notify via console, tray, or dialog)

However, they work well together:
- System tray can have a "Settings..." menu item
- System tray can show update notifications
- Settings UI can include auto-update preferences

---

## Recommended Implementation Order

### Option 1: User-Facing Features First
1. **System Tray UI** - Most visible improvement to user experience
2. **Settings UI** - Makes app more accessible to non-technical users
3. **Auto-Update** - Convenience feature, least critical

### Option 2: Backend First
1. **Settings UI** - Establishes config.json format and settings loading
2. **System Tray UI** - Uses settings from config.json
3. **Auto-Update** - Can add update preferences to existing settings

---

## Current Status Summary

| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Output Directory Config | ✅ Implemented | ❌ No GUI | Partially Done |
| Opponent Tracking Config | ✅ Implemented | ❌ No GUI | Partially Done |
| System Tray | N/A | ❌ No Implementation | Not Started |
| Settings Dialog | ❌ No config.json | ❌ No GUI | Not Started |
| Auto-Update | ❌ No Implementation | ❌ No Implementation | Not Started |

---

## Implementation Notes

All three features are part of **Phase 5: System Tray UI & User Controls**, which is currently **not implemented**. The core telemetry logging functionality (Phases 1-4, 6) is complete and working.

**Current Status**: Application runs as `example_app.py` command-line tool
**After Phase 5**: Application would run as background service with system tray UI, settings dialog, and auto-update capability

---

## See Also

- `feature_system_tray.md` - Detailed specification for system tray integration
- `feature_settings_ui.md` - Detailed specification for settings dialog
- `feature_auto_update.md` - Detailed specification for auto-update functionality
- `.claude/CLAUDE.md` - Phase 5 overview and success criteria
