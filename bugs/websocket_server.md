# WebSocket Server Implementation

**Date Created:** 2025-11-22
**Priority:** High
**Component:** Dashboard Server - Communication
**Phase:** Phase 1 MVP

## Description

Implement Flask-SocketIO server to handle bidirectional communication between monitor (data source) and dashboards (viewers).

## Requirements

### Must Have - Monitor Communication
1. Accept WebSocket connections from monitor
2. Handle `request_session_id` event → respond with UUID
3. Handle `setup_data` event → store and broadcast to dashboards
4. Handle `telemetry_update` event → store and broadcast to dashboards
5. Emit `session_id_assigned` event to monitor

### Must Have - Dashboard Communication
1. Accept WebSocket connections from browser dashboards
2. Handle `join_session` event → add client to session room
3. Emit `setup_update` event when setup received
4. Emit `telemetry_update` event when telemetry received (2Hz)
5. Send current session data on join (if available)

### Must Have - General
1. Connection/disconnection logging
2. Room-based broadcasting (one room per session ID)
3. CORS enabled for browser access
4. Graceful error handling

### Nice to Have
1. Authentication/authorization for dashboards
2. Rate limiting to prevent abuse
3. Compression for large payloads
4. Heartbeat/ping-pong for connection health

## Technical Details

**File:** `app/main.py`

**WebSocket Events:**

**From Monitor:**
```python
@socketio.on('request_session_id')
# Payload: {}
# Response: emit('session_id_assigned', {'session_id': UUID})

@socketio.on('setup_data')
# Payload: {'session_id': str, 'timestamp': ISO, 'setup': Dict}
# Action: Store setup + broadcast to room

@socketio.on('telemetry_update')
# Payload: {'session_id': str, 'telemetry': Dict}
# Action: Store telemetry + broadcast to room (2Hz)
```

**From Dashboard:**
```python
@socketio.on('join_session')
# Payload: {'session_id': str}
# Action: join_room(session_id) + send current data
```

**Server Events:**
```python
@socketio.on('connect')
# Log connection

@socketio.on('disconnect')
# Log disconnection
```

## Success Criteria

- [x] Monitor connects and receives session ID
- [x] Monitor can publish setup data
- [x] Monitor can publish telemetry (2Hz)
- [x] Dashboards can join session rooms
- [x] Setup broadcasts to all dashboards in room
- [x] Telemetry broadcasts to all dashboards in room
- [x] Multiple dashboards can view same session
- [x] Reconnection works after disconnect
- [ ] Integration tests pass (test_websocket.py)

## Testing

**Test File:** `tests/test_websocket.py`

**Test Cases:**
```python
def test_websocket_connect()              # Connection succeeds
def test_request_session_id()             # UUID returned
def test_setup_data_storage()             # Setup stored
def test_setup_broadcast()                # Broadcast to dashboards
def test_telemetry_update()               # Telemetry broadcast
def test_join_session()                   # Dashboard joins room
def test_join_session_with_data()         # Receives current data
def test_multiple_dashboards()            # Multiple viewers work
def test_reconnect_after_disconnect()     # Reconnection works
```

## Dependencies

- `flask` >= 2.3.0
- `flask-socketio` >= 5.3.0
- `python-socketio` >= 5.9.0
- `eventlet` or `gevent` (async mode)

## Related Files

- `app/__init__.py` - Flask app factory + socketio init
- `app/session_manager.py` - Session data storage
- `run.py` - Server entry point
- `tests/test_websocket.py` - Integration tests

## API Contract

See RACE_DASHBOARD_PLAN.md lines 1244-1378 for complete API specification.

**Monitor → Server:**
- `request_session_id` → `session_id_assigned`
- `setup_data` (once per session)
- `telemetry_update` (2Hz)

**Server → Dashboard:**
- `setup_update` (on join + when received)
- `telemetry_update` (2Hz)

**Dashboard → Server:**
- `join_session` → room joined + current data sent

## Error Handling

**Connection Failures:**
- Log error and continue serving other clients
- No crash on single client disconnect

**Invalid Data:**
- Validate session_id exists before broadcasting
- Log warning for malformed payloads
- Continue processing (don't crash)

**Room Broadcasting:**
- Use `room=session_id` to broadcast only to relevant dashboards
- Handle empty rooms gracefully (no viewers yet)

## Performance Considerations

**Update Rate:**
- Telemetry: 2Hz (every 500ms)
- Setup: Once per session
- Expected clients: 1 monitor + 5-10 dashboards per session

**Bandwidth:**
- Telemetry payload: ~1-2KB JSON
- Per session: ~4KB/sec (2 updates × 2KB)
- 10 dashboards: ~40KB/sec per session

## Notes

**CORS Configuration:**
```python
socketio.init_app(app, cors_allowed_origins="*")
```
⚠️ Phase 1: Allow all origins (development)
🔒 Future: Restrict to specific domains for production

**Async Mode:**
- Use `eventlet` or `gevent` for async worker
- Required for WebSocket support
- Configured in socketio.run()

## References

- RACE_DASHBOARD_PLAN.md - Lines 444-531 (WebSocket implementation)
- RACE_DASHBOARD_PLAN.md - Lines 1244-1378 (API contracts)
- Flask-SocketIO docs: https://flask-socketio.readthedocs.io/
