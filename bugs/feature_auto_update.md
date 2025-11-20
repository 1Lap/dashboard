# Feature: Auto-Update from GitHub

**Status**: Not Implemented
**Priority**: Low
**Category**: Maintenance & Distribution
**Estimated Effort**: 3-5 days
**Complexity**: High

---

## Description

Add automatic update checking and installation from the GitHub repository so users always have the latest version without manual downloads.

**Current**: Users must manually download new releases from GitHub
**Desired**: App checks for updates and offers to install them automatically

## User Story

As a user, I want the app to update itself automatically so that:
- I don't have to manually check GitHub for new versions
- I get bug fixes and new features without effort
- I don't have to reinstall or reconfigure the app
- My settings are preserved across updates

## Requirements

### Must Have

1. **Update Check on Startup**
   - On app launch, check GitHub for latest release
   - Compare current version with latest release version
   - Non-blocking (don't delay app startup)
   - Handle offline/network errors gracefully

2. **Update Notification**
   - If update available, show notification:
     - "Update available: v1.2.0 → v1.3.0"
     - "View changes" link (opens release notes)
     - "Download and install" button
     - "Skip this version" button
     - "Remind me later" button

3. **Download and Install**
   - Download new .exe from GitHub release
   - Verify download integrity (checksum)
   - Replace current .exe with new one
   - Restart application

4. **Version Management**
   - Track current version in app
   - Parse version from GitHub release tags
   - Support semantic versioning (v1.2.3)

### Nice to Have

1. **Manual Update Check**
   - Menu item: "Check for Updates..."
   - Force check even if auto-check disabled

2. **Auto-Update Settings**
   - "Automatically download and install updates" (checkbox)
   - "Check for updates on startup" (checkbox)
   - "Include pre-release versions" (checkbox)

3. **Update History**
   - Show changelog/release notes in dialog
   - List of previous versions installed

4. **Rollback**
   - Keep previous .exe as backup
   - "Rollback to previous version" option if update fails

5. **Silent Updates**
   - Download in background
   - Install on next app restart (no interruption)

## Technical Challenges

### Challenge 1: Replacing Running Executable

**Problem**: Can't replace .exe file while it's running on Windows

**Solutions**:

**Option A: External Updater Script** (Recommended)
1. Download new .exe to temp location
2. Launch updater script (Python or batch file)
3. Exit main app
4. Updater script waits for app to exit
5. Updater replaces old .exe with new .exe
6. Updater relaunches app
7. Updater deletes itself

**Option B: Rename and Replace**
1. Rename current .exe to `app.exe.old`
2. Download new .exe as `app.exe`
3. On next restart, delete `app.exe.old`

**Option C: Use pyupdater library**
- Third-party library designed for this
- Handles signing, patches, rollbacks
- More complex setup

### Challenge 2: Code Signing

**Problem**: Windows SmartScreen flags unsigned .exe files

**Solutions**:
- Purchase code signing certificate ($200-$400/year)
- Sign .exe files with certificate
- Or: Document that users should "Run anyway" on first launch

### Challenge 3: Update Security

**Problem**: Prevent malicious updates (man-in-the-middle attacks)

**Solutions**:
- Verify SSL certificate when downloading (HTTPS)
- Check SHA256 checksum of downloaded file
- Optionally: GPG signature verification
- Only download from official GitHub releases

### Challenge 4: Settings Preservation

**Problem**: Don't lose user settings when updating

**Solutions**:
- Store settings in separate `config.json` (already planned)
- Settings file is NOT replaced during update
- Only replace .exe file, preserve all other files

## Technical Implementation

### Version Management

```python
# In src/__init__.py or src/version.py
__version__ = "1.0.0"

def get_current_version():
    """Get current app version"""
    return __version__

def parse_version(version_str):
    """Parse version string to tuple (major, minor, patch)"""
    # "v1.2.3" -> (1, 2, 3)
    version = version_str.lstrip('v')
    return tuple(map(int, version.split('.')))

def compare_versions(current, latest):
    """Compare versions, return True if update available"""
    return parse_version(latest) > parse_version(current)
```

### GitHub API Integration

```python
# New file: src/updater.py

import requests
import hashlib
from pathlib import Path

class UpdateChecker:
    """Check for updates from GitHub releases"""

    REPO_OWNER = "davedean"
    REPO_NAME = "eztel-writer"
    GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

    def check_for_update(self, current_version):
        """
        Check if update is available

        Returns:
            dict: {'available': bool, 'version': str, 'download_url': str, 'changelog': str}
            or None if check fails
        """
        try:
            response = requests.get(self.GITHUB_API, timeout=5)
            response.raise_for_status()
            release = response.json()

            latest_version = release['tag_name']  # e.g., "v1.2.0"
            download_url = None
            checksum = None

            # Find .exe asset in release
            for asset in release['assets']:
                if asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break

            if not download_url:
                return None

            return {
                'available': compare_versions(current_version, latest_version),
                'current_version': current_version,
                'latest_version': latest_version,
                'download_url': download_url,
                'changelog': release['body'],  # Release notes
                'published_at': release['published_at'],
            }

        except (requests.RequestException, KeyError, ValueError) as e:
            # Network error, API error, or parsing error
            return None

    def download_update(self, download_url, dest_path):
        """
        Download update file

        Returns:
            bool: True if download successful
        """
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True
        except requests.RequestException:
            return False

    def verify_checksum(self, file_path, expected_checksum):
        """Verify downloaded file integrity"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_checksum
```

### Updater Script

```python
# updater.py (separate script, not packaged in main .exe)

import sys
import time
import shutil
from pathlib import Path

def update_app(old_exe, new_exe):
    """
    Replace old .exe with new .exe

    Args:
        old_exe: Path to current running .exe
        new_exe: Path to downloaded new .exe
    """
    # Wait for old app to exit
    time.sleep(2)

    # Backup old exe
    backup_exe = old_exe.with_suffix('.exe.old')
    if backup_exe.exists():
        backup_exe.unlink()
    shutil.move(old_exe, backup_exe)

    # Move new exe to old location
    shutil.move(new_exe, old_exe)

    # Restart app
    import subprocess
    subprocess.Popen([str(old_exe)])

    # Exit updater
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: updater.py <old_exe> <new_exe>")
        sys.exit(1)

    old_exe = Path(sys.argv[1])
    new_exe = Path(sys.argv[2])
    update_app(old_exe, new_exe)
```

### Integration with App

```python
# In example_app.py or tray_app.py

class TelemetryApp:
    def __init__(self):
        # ... existing init ...

        # Check for updates on startup (async, non-blocking)
        import threading
        update_thread = threading.Thread(target=self.check_for_updates_async)
        update_thread.daemon = True
        update_thread.start()

    def check_for_updates_async(self):
        """Check for updates in background"""
        from src.updater import UpdateChecker
        from src.version import get_current_version

        checker = UpdateChecker()
        update_info = checker.check_for_update(get_current_version())

        if update_info and update_info['available']:
            # Show notification or dialog
            self.show_update_notification(update_info)

    def show_update_notification(self, update_info):
        """Show update available notification"""
        # If using system tray: balloon notification
        # If using GUI: dialog box
        # Options: Download & Install, Skip, Later

    def download_and_install_update(self, download_url):
        """Download and install update"""
        from src.updater import UpdateChecker
        import tempfile
        import subprocess

        checker = UpdateChecker()

        # Download to temp directory
        temp_dir = Path(tempfile.gettempdir())
        new_exe = temp_dir / "LMU_Telemetry_Logger_new.exe"

        if checker.download_update(download_url, new_exe):
            # Launch updater script
            current_exe = Path(sys.executable)  # or Path(__file__) if not frozen
            subprocess.Popen([
                sys.executable,  # Python interpreter
                'updater.py',
                str(current_exe),
                str(new_exe)
            ])

            # Exit app (updater will replace and restart)
            self.quit()
```

## Testing Requirements

### Manual Testing

1. **Update Check**:
   - Start app with internet connection
   - Verify update check completes without errors
   - Mock GitHub API to simulate update available

2. **Download Update**:
   - Trigger update download
   - Verify file downloads to temp directory
   - Verify progress indicator (if implemented)

3. **Install Update**:
   - Complete update installation
   - Verify app restarts with new version
   - Verify settings preserved
   - Verify old .exe backed up

4. **Offline Handling**:
   - Start app without internet
   - Verify app works normally
   - Verify no error dialogs shown

### Automated Testing

```python
# tests/test_updater.py

def test_check_for_update_with_new_version():
    """Test update check when new version available"""

def test_check_for_update_with_same_version():
    """Test update check when no update available"""

def test_check_for_update_offline():
    """Test update check when offline"""

def test_download_update():
    """Test downloading update file"""

def test_verify_checksum():
    """Test checksum verification"""
```

## Dependencies

### Required

- **requests**: HTTP library for GitHub API
  ```
  pip install requests
  ```

### Optional

- **pyupdater**: Complete update framework (if using Option C)
  ```
  pip install pyupdater
  ```

## Files to Create

- `src/version.py` - Version management utilities
- `src/updater.py` - Update checking and downloading
- `updater.py` - External updater script (not packaged in .exe)
- `tests/test_updater.py` - Unit tests

## Files to Modify

- `example_app.py` (or `tray_app.py`) - Add update check on startup
- `requirements.txt` - Add `requests`
- `build.bat` - Include version in .exe metadata

## Implementation Steps

1. **Add version management** (1-2 hours)
   - Create `src/version.py`
   - Implement version comparison logic
   - Add version to app startup log

2. **Implement update checker** (3-4 hours)
   - Create `src/updater.py`
   - GitHub API integration
   - Download functionality
   - Checksum verification

3. **Create updater script** (2-3 hours)
   - Write `updater.py`
   - Test .exe replacement logic
   - Test restart functionality

4. **Integrate with app** (2-3 hours)
   - Add update check on startup
   - Create update notification dialog
   - Wire up "Download & Install" button

5. **Test and polish** (3-5 hours)
   - Test full update cycle
   - Test offline scenarios
   - Test update failure handling
   - Write unit tests

## Acceptance Criteria

- [ ] App checks for updates on startup (non-blocking)
- [ ] Update notification shown when new version available
- [ ] "Download & Install" downloads new .exe
- [ ] Downloaded .exe is verified (checksum)
- [ ] Old .exe is replaced with new .exe
- [ ] App restarts after update
- [ ] Settings preserved after update
- [ ] Old .exe backed up in case of failure
- [ ] Offline mode works without errors
- [ ] Manual "Check for Updates" menu item works

## Security Considerations

1. **HTTPS Only**: Only download from HTTPS URLs
2. **Checksum Verification**: Verify SHA256 checksum (if provided in release)
3. **Code Signing**: Sign .exe files to avoid SmartScreen warnings
4. **No Auto-Install**: Require user confirmation before installing updates
5. **Rollback**: Keep backup of previous version

## Notes

- **Independent Feature**: This feature is completely independent of system tray and settings UI
- **Optional**: App works fine without auto-update
- **Complexity**: Most complex of the Phase 5 features due to security and .exe replacement challenges
- **Alternative**: Users can manually download from GitHub (current method)

## Related Issues

- `feature_system_tray.md` - Could add "Check for Updates" menu item
- `feature_settings_ui.md` - Could add auto-update preferences
- Phase 5 in `CLAUDE.md` - This is one component of Phase 5

## References

- [GitHub API - Releases](https://docs.github.com/en/rest/releases/releases)
- [pyupdater Documentation](https://www.pyupdater.org/)
- [Windows Code Signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
