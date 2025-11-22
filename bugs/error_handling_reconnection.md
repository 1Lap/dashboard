# Error Handling and Reconnection Logic

**Date Created:** 2025-11-22
**Priority:** Medium
**Component:** Dashboard Server - Reliability
**Phase:** Phase 2 Polish

## Description

Implement robust error handling and automatic reconnection logic for both monitor-to-server and dashboard-to-server connections to ensure reliability during race sessions.

## Requirements

### Must Have - Monitor Reconnection
1. Detect connection loss to server
2. Automatic reconnection with exponential backoff
3. Resume publishing after reconnection
4. Maintain same session ID after reconnect
5. Re-send setup data after reconnect (if needed)
6. Log connection status changes

### Must Have - Dashboard Reconnection
1. Detect WebSocket disconnection
2. Automatic reconnection attempts
3. Update UI connection status indicator
4. Re-join session room after reconnect
5. Request latest data after reconnect
6. Show stale data warning during disconnect

### Must Have - Server Error Handling
1. Validate session IDs before broadcasting
2. Handle malformed WebSocket payloads gracefully
3. Log errors without crashing
4. Continue serving other clients on individual client errors
5. Handle missing/invalid data fields

### Nice to Have
1. Configurable reconnection parameters
2. Connection quality indicator (latency, packet loss)
3. Offline mode with cached data
4. Heartbeat/ping mechanism
5. Circuit breaker pattern for repeated failures

## Technical Details

### Monitor Reconnection Logic

**File:** `src/dashboard_publisher.py` (monitor repo)

**Reconnection Strategy:**
```python
class DashboardPublisher:
    def __init__(self, ...):
        self.reconnect_delay = 1.0      # Start with 1 second
        self.max_reconnect_delay = 60.0 # Max 60 seconds
        self.reconnect_attempts = 0

    def connect_with_retry(self):
        while True:
            try:
                self.sio.connect(self.server_url)
                self.reconnect_delay = 1.0       # Reset on success
                self.reconnect_attempts = 0
                break
            except Exception as e:
                self.reconnect_attempts += 1
                print(f"Connection failed (attempt {self.reconnect_attempts}): {e}")
                print(f"Retrying in {self.reconnect_delay}s...")
                time.sleep(self.reconnect_delay)

                # Exponential backoff: 1s → 2s → 4s → 8s → ... → 60s
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_reconnect_delay
                )
```

**Disconnect Handler:**
```python
@self.sio.event
def disconnect():
    print("[Publisher] Disconnected from server")
    print("[Publisher] Attempting to reconnect...")
    self.connected = False
    self.connect_with_retry()  # Auto-reconnect
```

### Dashboard Reconnection Logic

**File:** `static/js/dashboard.js`

**Auto-Reconnect:**
```javascript
socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateConnectionStatus(false);

    // Socket.IO handles reconnection automatically
    // Just update UI and wait for 'connect' event
});

socket.on('connect', () => {
    console.log('Reconnected to server');
    updateConnectionStatus(true);

    // Re-join session room
    socket.emit('join_session', {session_id: sessionId});
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    // Socket.IO will retry automatically
});
```

**Stale Data Warning:**
```javascript
let lastUpdate = Date.now();

socket.on('telemetry_update', (data) => {
    lastUpdate = Date.now();
    updateTelemetry(data.telemetry);
});

// Check for stale data every 5 seconds
setInterval(() => {
    const secondsSinceUpdate = (Date.now() - lastUpdate) / 1000;

    if (secondsSinceUpdate > 5) {
        showStaleDataWarning(secondsSinceUpdate);
    } else {
        hideStaleDataWarning();
    }
}, 5000);
```

### Server Error Handling

**File:** `app/main.py`

**Validate Session ID:**
```python
@socketio.on('setup_data')
def handle_setup(data):
    try:
        session_id = data.get('session_id')
        if not session_id:
            print("[Server] ERROR: Missing session_id in setup_data")
            return

        setup = data.get('setup', {})
        timestamp = data.get('timestamp')

        session_mgr.update_setup(session_id, setup, timestamp)
        emit('setup_update', data, room=session_id)

    except Exception as e:
        print(f"[Server] ERROR handling setup_data: {e}")
        # Don't crash - log and continue
```

**Malformed Payload Handling:**
```python
@socketio.on('telemetry_update')
def handle_telemetry(data):
    try:
        session_id = data.get('session_id')
        telemetry = data.get('telemetry')

        if not session_id or not telemetry:
            print("[Server] ERROR: Invalid telemetry payload")
            return

        # Validate telemetry has required fields
        required_fields = ['lap', 'fuel', 'position']
        if not all(field in telemetry for field in required_fields):
            print("[Server] WARNING: Telemetry missing required fields")
            # Continue anyway - dashboard will handle missing data

        session_mgr.update_telemetry(session_id, telemetry)
        emit('telemetry_update', data, room=session_id)

    except Exception as e:
        print(f"[Server] ERROR handling telemetry: {e}")
```

## Success Criteria

### Monitor
- [x] Reconnects automatically on disconnect
- [x] Uses exponential backoff (1s → 60s)
- [x] Resumes publishing after reconnect
- [x] Logs reconnection attempts
- [ ] Re-sends setup data if needed
- [ ] Tests pass (test_reconnection.py)

### Dashboard
- [x] Shows connection status in UI
- [x] Auto-reconnects on disconnect
- [x] Re-joins session after reconnect
- [x] Shows stale data warning (>5s)
- [ ] Requests latest data after reconnect
- [ ] Manual testing passes

### Server
- [x] Validates all payloads
- [x] Handles errors without crashing
- [x] Logs errors clearly
- [x] Continues serving other clients
- [ ] Integration tests pass

## Testing

**Test File:** `tests/test_reconnection.py`

**Monitor Tests:**
```python
def test_monitor_auto_reconnect()         # Reconnects after disconnect
def test_monitor_exponential_backoff()    # Backoff increases correctly
def test_monitor_resume_publishing()      # Publishes after reconnect
def test_monitor_max_backoff()            # Caps at max_reconnect_delay
```

**Dashboard Tests:**
```python
def test_dashboard_connection_status()    # UI updates on disconnect
def test_dashboard_auto_rejoin()          # Re-joins session
def test_dashboard_stale_data_warning()   # Shows warning after 5s
```

**Server Tests:**
```python
def test_invalid_session_id()             # Handles gracefully
def test_malformed_payload()              # Logs and continues
def test_missing_required_fields()        # Handles partial data
def test_multiple_clients_on_error()      # Other clients unaffected
```

**Manual Testing Checklist:**
- [ ] Kill monitor → restart → same session ID
- [ ] Kill server → restart → monitor reconnects
- [ ] Disconnect network → reconnect → data resumes
- [ ] Dashboard disconnect → reconnect → rejoins session
- [ ] Send invalid data → server logs error, continues
- [ ] Multiple dashboards → one disconnects → others unaffected

## Error Messages

**Monitor Console:**
```
[Publisher] Connection failed (attempt 1): Connection refused
[Publisher] Retrying in 1.0s...
[Publisher] Connection failed (attempt 2): Connection refused
[Publisher] Retrying in 2.0s...
[Publisher] Connected to http://localhost:5000
```

**Dashboard UI:**
```
🔴 Disconnected (attempting to reconnect...)
⚠️ Data may be stale (last update 12 seconds ago)
🟢 Connected
```

**Server Logs:**
```
[Server] ERROR: Missing session_id in setup_data
[Server] WARNING: Telemetry missing required fields: ['position']
[Server] ERROR handling telemetry: KeyError: 'session_id'
[Server] Client disconnected: abc123
[Server] Client connected: def456
```

## Configuration

**Monitor Config (config.json):**
```json
{
  "reconnect_delay_initial": 1.0,
  "reconnect_delay_max": 60.0,
  "connection_timeout": 10.0
}
```

**Dashboard Config (JavaScript constants):**
```javascript
const STALE_DATA_THRESHOLD = 5000;  // 5 seconds
const RECONNECT_ATTEMPTS = Infinity; // Retry forever
```

## Related Files

**Monitor (separate repo):**
- `src/dashboard_publisher.py` - Publisher with reconnection

**Server (this repo):**
- `app/main.py` - Error handling in WebSocket handlers
- `static/js/dashboard.js` - Dashboard reconnection logic
- `tests/test_reconnection.py` - Reconnection tests

## Performance Impact

**Reconnection Overhead:**
- Initial reconnect: 1 second delay
- Max reconnect: 60 second delay
- Negligible impact on other clients

**Error Handling:**
- Validation adds <1ms per message
- Logging adds <1ms per error
- No impact on successful operations

## Security Considerations

**Rate Limiting (Future):**
- Prevent reconnection spam attacks
- Limit failed connection attempts per IP
- Exponential backoff helps naturally

**Error Information Disclosure:**
- Don't expose internal errors to clients
- Log detailed errors server-side only
- Return generic errors to clients

## References

- RACE_DASHBOARD_PLAN.md - Lines 1180-1197 (Phase 2 requirements)
- RACE_DASHBOARD_PLAN.md - Lines 1520-1545 (Manual testing)
- Socket.IO reconnection docs: https://socket.io/docs/v4/client-initialization/#reconnection
