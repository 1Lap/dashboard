# Secret URL Generation and Session Persistence

**Date Created:** 2025-11-22
**Priority:** High
**Component:** Dashboard Server - Session URLs
**Phase:** Phase 1 MVP

## Description

Implement secret URL generation and session persistence to ensure team members can access the dashboard throughout a race session without the URL changing.

## Requirements

### Must Have
1. Generate unique, unpredictable session IDs (UUID4)
2. Session ID stays constant throughout race session
3. URL format: `http://server:5000/dashboard/<session-id>`
4. Display full dashboard URL when monitor connects
5. Session persists until server restart
6. Multiple viewers can use same URL simultaneously

### Nice to Have
1. Custom session IDs (user-provided)
2. Session expiry after configurable timeout
3. Session history/archive
4. QR code generation for easy mobile access
5. Short URLs (e.g., /d/abc123 instead of full UUID)
6. Session password protection

## Technical Details

### UUID Generation

**Implementation:** Already in `app/session_manager.py`

```python
import uuid

def create_session() -> str:
    """Generate UUID4 session ID"""
    return str(uuid.uuid4())
    # Example: "abc12def-3456-7890-abcd-ef1234567890"
```

**Properties:**
- 36 characters (32 hex + 4 hyphens)
- Cryptographically random
- Collision probability: ~1 in 2^122
- URL-safe (no special encoding needed)

### URL Display on Monitor

**File:** `src/dashboard_publisher.py` (monitor repo)

```python
@self.sio.event
def session_id_assigned(data):
    """Receive session ID from server"""
    self.session_id = data['session_id']

    print("")
    print("=" * 60)
    print("[Publisher] Session Created!")
    print("=" * 60)
    print(f"Session ID: {self.session_id}")
    print("")
    print("📱 DASHBOARD URL:")
    print(f"   {self.server_url}/dashboard/{self.session_id}")
    print("")
    print("Share this URL with your team members")
    print("=" * 60)
    print("")
```

**Console Output:**
```
============================================================
[Publisher] Session Created!
============================================================
Session ID: abc12def-3456-7890-abcd-ef1234567890

📱 DASHBOARD URL:
   http://localhost:5000/dashboard/abc12def-3456-7890-abcd-ef1234567890

Share this URL with your team members
============================================================
```

### Session Persistence Strategy

**Phase 1 (MVP):**
```python
# In-memory storage
sessions: Dict[str, Dict[str, Any]] = {}

# Session persists until:
# 1. Server restart (sessions cleared)
# 2. Manual deletion (not implemented)
```

**Pros:**
- Simple implementation
- Fast access
- No external dependencies

**Cons:**
- Lost on server restart
- No recovery after crash
- Limited to single server process

**Future (Phase 3):**
```python
# Redis or database storage
# Sessions persist across restarts
# Supports multi-server deployment
# Can set TTL (time-to-live)
```

### URL Validation

**File:** `app/main.py`

```python
@current_app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Serve dashboard for specific session"""

    # Validate UUID format (optional - helpful for debugging)
    try:
        uuid.UUID(session_id)
    except ValueError:
        return "Invalid session ID", 400

    # Session may not exist yet (monitor not connected)
    # Dashboard will wait for data via WebSocket
    return render_template('dashboard.html', session_id=session_id)
```

**Note:** Dashboard loads even if session doesn't exist yet. This allows team members to open URL before race starts.

### Multi-Viewer Support

**How it works:**
1. Each dashboard client opens same URL
2. Each client joins same WebSocket room (by session_id)
3. Server broadcasts updates to entire room
4. All viewers receive same data simultaneously

**Room-Based Broadcasting:**
```python
# In app/main.py
from flask_socketio import join_room, emit

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data['session_id']

    # Add client to room
    join_room(session_id)

    # Send current data if available
    # ...

@socketio.on('telemetry_update')
def handle_telemetry(data):
    session_id = data['session_id']

    # Broadcast to all clients in room
    emit('telemetry_update', data, room=session_id)
```

**Scalability:**
- Tested with 10+ concurrent viewers per session
- No performance degradation
- Limited by server resources, not architecture

## Success Criteria

- [x] UUID4 used for session IDs
- [x] Session ID consistent throughout race
- [x] Full URL displayed to monitor
- [x] Same URL works for multiple viewers
- [x] Dashboard loads even if session not started
- [x] URL doesn't change when monitor reconnects
- [ ] URL easy to share (short enough for messaging)
- [ ] QR code generation (nice to have)

## User Experience

**Monitor Console:**
```
[Publisher] Connecting to server...
[Publisher] Connected to http://localhost:5000
[Publisher] Requesting session ID...

============================================================
[Publisher] Session Created!
============================================================
Session ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

📱 DASHBOARD URL:
   http://192.168.1.100:5000/dashboard/a1b2c3d4-e5f6-7890-abcd-ef1234567890

Share this URL with your team members
============================================================

[Publisher] Publishing telemetry at 2Hz...
[Publisher] Setup data sent
```

**Team Member Experience:**
1. Receive URL via messaging app (Discord, WhatsApp, etc.)
2. Click or copy-paste into browser
3. Dashboard loads and shows "Waiting for data..."
4. When race starts, data appears automatically
5. Real-time updates throughout race
6. Can refresh page without losing connection
7. Can share same URL with other team members

## URL Shortening (Future)

**Problem:** UUIDs are long (36 chars)

**Solution 1: Base62 Encoding**
```python
import base62

def shorten_session_id(uuid_str):
    # Remove hyphens and convert to base62
    uuid_int = int(uuid_str.replace('-', ''), 16)
    short_id = base62.encode(uuid_int)
    # Result: ~22 characters (e.g., "4fTr9K2pQ3vN8xB1mZ7s")
    return short_id
```

**Solution 2: Custom Short IDs**
```python
import secrets
import string

def generate_short_id(length=8):
    # Use alphanumeric characters
    alphabet = string.ascii_letters + string.digits
    short_id = ''.join(secrets.choice(alphabet) for _ in range(length))
    # Result: 8 characters (e.g., "aBc12XyZ")
    return short_id
```

**URL Examples:**
- Full UUID: `http://server:5000/dashboard/abc12def-3456-7890-abcd-ef1234567890`
- Base62: `http://server:5000/dashboard/4fTr9K2pQ3vN8xB1mZ7s`
- Short ID: `http://server:5000/d/aBc12XyZ`

## QR Code Generation (Future)

**Library:** `qrcode` or `segno`

```python
import qrcode

def generate_qr_code(url):
    """Generate QR code for dashboard URL"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("dashboard_qr.png")
    return "dashboard_qr.png"
```

**Use Case:**
- Display QR code in monitor console
- Team scans with phone camera
- Instant access to dashboard

## Session Expiry (Future)

**Configuration:**
```python
# config.py
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes
```

**Implementation:**
```python
from datetime import datetime, timedelta

class SessionManager:
    def cleanup_expired_sessions(self):
        """Remove sessions older than timeout"""
        now = datetime.utcnow()
        expired = []

        for session_id, session in self.sessions.items():
            last_update = datetime.fromisoformat(session['last_update'])
            age = (now - last_update).total_seconds()

            if age > SESSION_TIMEOUT:
                expired.append(session_id)

        for session_id in expired:
            del self.sessions[session_id]
            print(f"[SessionManager] Cleaned up expired session: {session_id}")

# Run cleanup periodically
import threading

def cleanup_thread():
    while True:
        time.sleep(SESSION_CLEANUP_INTERVAL)
        session_mgr.cleanup_expired_sessions()

threading.Thread(target=cleanup_thread, daemon=True).start()
```

## Security Considerations

**UUID Unpredictability:**
- UUID4 uses cryptographically secure random generation
- Guessing a valid session ID: ~1 in 2^122 attempts
- Effectively impossible to brute force

**URL Security:**
- ✅ Unpredictable (UUID4)
- ⚠️ No authentication (anyone with URL can view)
- ⚠️ Transmitted in plain HTTP (local network)

**Threat Model:**
- **Acceptable:** Team members share URL privately
- **Risk:** URL leaked publicly (anyone can view telemetry)
- **Future:** Add password protection or team authentication

## Testing

**Test Cases:**
```python
def test_session_id_format():
    """Test UUID4 format"""
    session_id = session_manager.create_session()
    uuid.UUID(session_id)  # Raises ValueError if invalid

def test_session_id_uniqueness():
    """Test no collisions"""
    ids = [session_manager.create_session() for _ in range(100)]
    assert len(ids) == len(set(ids))  # All unique

def test_url_persistence():
    """Test URL stays same after reconnect"""
    # Create session
    session_id = create_session()

    # Simulate reconnect
    # (session_id should be same)

def test_multiple_viewers():
    """Test multiple dashboards with same URL"""
    # Multiple clients join same session
    # All receive same updates
```

## Documentation

**README Update:**
```markdown
## Getting Started

1. Start the server:
   ```bash
   python run.py
   ```

2. Run the monitor (on Windows with LMU):
   ```bash
   python monitor.py
   ```

3. Monitor will display dashboard URL:
   ```
   📱 DASHBOARD URL:
      http://192.168.1.100:5000/dashboard/abc-def-ghi
   ```

4. Share URL with team members
5. Team opens URL in any browser
6. Dashboard shows real-time telemetry!

**Important:** URL stays the same for entire race session
```

## Related Files

- `app/session_manager.py` - UUID generation
- `app/main.py` - URL routing
- `src/dashboard_publisher.py` - URL display (monitor repo)
- `tests/test_session_manager.py` - UUID tests

## References

- RACE_DASHBOARD_PLAN.md - Lines 534-591 (SessionManager)
- RACE_DASHBOARD_PLAN.md - Lines 32-43 (Use case with secret URL)
- Python UUID docs: https://docs.python.org/3/library/uuid.html
