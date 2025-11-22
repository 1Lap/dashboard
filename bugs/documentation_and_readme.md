# Documentation and README

**Date Created:** 2025-11-22
**Priority:** Medium
**Component:** Dashboard Server - Documentation
**Phase:** Phase 2 Polish

## Description

Create comprehensive documentation for the dashboard server including README, installation guide, usage instructions, troubleshooting, and API documentation.

## Requirements

### Must Have
1. **README.md** - Project overview and quick start
2. **INSTALLATION.md** - Detailed installation steps
3. **USAGE.md** - How to use the dashboard
4. **DEPLOYMENT.md** - Deployment options (local/cloud)
5. **API.md** - WebSocket API documentation
6. **TROUBLESHOOTING.md** - Common issues and solutions

### Nice to Have
1. Architecture diagrams
2. Video tutorial
3. FAQ section
4. Contributing guide
5. Change log
6. Screenshots/GIFs

## File Structure

```
server/
├── README.md                    # Main documentation
├── docs/
│   ├── INSTALLATION.md          # Installation guide
│   ├── USAGE.md                 # User guide
│   ├── DEPLOYMENT.md            # Deployment options
│   ├── API.md                   # API reference
│   ├── TROUBLESHOOTING.md       # Common issues
│   ├── ARCHITECTURE.md          # System design
│   └── images/
│       ├── dashboard_screenshot.png
│       ├── architecture.png
│       └── setup_flow.png
├── CONTRIBUTING.md              # How to contribute
└── CHANGELOG.md                 # Version history
```

## README.md Template

**File:** `README.md`

```markdown
# 1Lap Race Dashboard Server

Real-time telemetry dashboard for endurance racing teams. Monitor fuel, tire temperatures, pressures, and car setup from any device during the race.

![Dashboard Screenshot](docs/images/dashboard_screenshot.png)

## Features

- 🔴 **Real-time telemetry** - Fuel, tires, brakes, engine temps
- 🔧 **Car setup display** - View complete mechanical setup
- 📱 **Mobile friendly** - Works on phone, tablet, laptop
- 🔗 **Secret URLs** - Share with team via unique session link
- 🌐 **Multi-viewer** - Multiple team members can view simultaneously
- ⚡ **2Hz updates** - Near-instant data refresh

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/1Lap/server.git
cd server

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Server

```bash
python run.py
```

Server runs at: `http://localhost:5000`

### 3. Connect Monitor

See [monitor repository](https://github.com/1Lap/monitor) for data collection setup.

### 4. Access Dashboard

Monitor will display URL:
```
📱 DASHBOARD URL:
   http://192.168.1.100:5000/dashboard/abc-def-ghi
```

Share URL with team → they open in browser → real-time telemetry!

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup
- [Usage Guide](docs/USAGE.md) - How to use
- [Deployment Guide](docs/DEPLOYMENT.md) - Local/cloud hosting
- [API Reference](docs/API.md) - WebSocket API
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues

## Requirements

- Python 3.11+
- Flask 2.3+
- Flask-SocketIO 5.3+

## Architecture

```
Monitor (Windows + LMU) → Server (Flask) → Dashboards (Browsers)
      WebSocket              WebSocket
```

See [Architecture](docs/ARCHITECTURE.md) for details.

## Deployment Options

**Local Network** (simplest):
- Run on driver's PC
- Team connects via LAN

**Cloud Hosted**:
- Heroku, Railway, Render
- Accessible from anywhere
- See [Deployment Guide](docs/DEPLOYMENT.md)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Related Projects

- [monitor](https://github.com/1Lap/monitor) - Data collector for LMU
- [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) - Complete implementation plan

## Support

- GitHub Issues: [Report a bug](https://github.com/1Lap/server/issues)
- Documentation: [docs/](docs/)

---

Built with ❤️ for endurance racing teams
```

## INSTALLATION.md Template

**File:** `docs/INSTALLATION.md`

```markdown
# Installation Guide

Complete guide to installing the 1Lap Race Dashboard Server.

## Prerequisites

- Python 3.11 or newer
- pip (Python package manager)
- Git (for cloning repository)

## Step 1: Clone Repository

```bash
git clone https://github.com/1Lap/server.git
cd server
```

## Step 2: Create Virtual Environment (Recommended)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- Flask (web framework)
- Flask-SocketIO (WebSocket support)
- python-socketio (client library)
- eventlet (async server)

## Step 4: Configuration (Optional)

Copy environment template:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=5000
```

## Step 5: Verify Installation

```bash
python run.py
```

Expected output:
```
============================================================
1Lap Race Dashboard Server
============================================================
Server running at: http://localhost:5000
Waiting for monitor connections...
============================================================
```

Open browser: `http://localhost:5000`

You should see: "1Lap Race Dashboard Server - Waiting for sessions..."

## Troubleshooting

**"No module named flask"**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**"Port 5000 already in use"**
```bash
# Change port in .env or run.py
PORT=5001
```

**"Permission denied"**
```bash
# Use sudo (Linux/macOS) or run as administrator (Windows)
sudo python run.py
```

## Next Steps

- [Usage Guide](USAGE.md) - How to use the dashboard
- [Deployment Guide](DEPLOYMENT.md) - Deploy to production
- Install [monitor](https://github.com/1Lap/monitor) to send telemetry data
```

## USAGE.md Template

**File:** `docs/USAGE.md`

```markdown
# Usage Guide

How to use the 1Lap Race Dashboard.

## Workflow

### 1. Start Server

**Local Network (recommended for testing):**
```bash
python run.py
```

**Production (Gunicorn):**
```bash
gunicorn -c gunicorn_config.py run:app
```

### 2. Connect Monitor

On Windows PC with LMU:
```bash
cd ../monitor
python monitor.py
```

Monitor will:
1. Connect to server
2. Request session ID
3. Display dashboard URL
4. Start publishing telemetry (2Hz)

Console output:
```
============================================================
[Publisher] Session Created!
============================================================
Session ID: abc-def-ghi

📱 DASHBOARD URL:
   http://192.168.1.100:5000/dashboard/abc-def-ghi

Share this URL with your team members
============================================================
```

### 3. Share URL with Team

**Methods:**
- Copy-paste URL to Discord/WhatsApp/Telegram
- Text message
- QR code (future feature)

**Example:**
```
Hey team! Dashboard is live:
http://192.168.1.100:5000/dashboard/abc-def-ghi
```

### 4. Team Opens Dashboard

Team members:
1. Click or paste URL in browser
2. Dashboard loads automatically
3. Shows "Waiting for data..." until race starts
4. Real-time updates appear when telemetry flows

**Supported Browsers:**
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

### 5. During the Race

**Dashboard shows:**
- 📊 Session info (driver, car, track, position, lap)
- ⛽ Fuel (liters, percentage, estimated laps)
- 🔥 Tire temperatures (FL, FR, RL, RR)
- 💨 Tire pressures (FL, FR, RL, RR)
- 🔴 Brake temperatures
- 🌡️ Engine temperature
- 🌤️ Track & ambient temps
- 🔧 Car setup (captured at start)

**Connection status:**
- 🟢 Connected - Live data
- 🔴 Disconnected - Auto-reconnecting
- ⚠️ Stale data - No updates for >5 seconds

### 6. Multiple Viewers

Same URL works for everyone:
- Engineer on laptop
- Driver's coach on tablet
- Team manager on phone
- All see same data in real-time

### 7. After the Race

- Server keeps running (can view next session)
- Close browser tabs (data not saved)
- Restart monitor for new session (new URL)

## Dashboard UI Guide

### Header
- Session ID
- Connection status indicator

### Session Info
- Current position (e.g., "P3")
- Current lap / total laps
- Driver name, car, track

### Fuel Section
- Progress bar (color: red → orange → green)
- Liters remaining / capacity
- Percentage
- Estimated laps remaining (rough: 3L/lap)

### Tire Data
- 2×2 grid layout
- FL (front left), FR (front right)
- RL (rear left), RR (rear right)
- Temps in °C, pressures in PSI

### Setup Section
- Captured once at session start
- Shows full JSON from LMU REST API
- Suspension, aero, brakes, etc.

## Keyboard Shortcuts

(Future feature)
- `R` - Refresh
- `F` - Fullscreen
- `Esc` - Exit fullscreen

## Tips & Best Practices

1. **Stable URL** - URL stays same for entire session, bookmark it
2. **Refresh safe** - Can refresh page without losing data
3. **Mobile landscape** - Rotate phone horizontally for best view
4. **Multiple tabs** - Can open multiple views (fuel + tires)
5. **Screenshot friendly** - Dashboard looks good in screenshots

## Common Tasks

### Change Server Port
Edit `.env` or `run.py`:
```python
PORT = 5001
```

### Access from Different Network
Forward port on router (advanced):
```
External: 12345 → Internal: 192.168.1.100:5000
```

### Run in Background (Linux)
```bash
nohup python run.py &
```

### Check Active Sessions
Future feature - will show list of active sessions

## Troubleshooting

**"Disconnected" status:**
- Check monitor is running
- Check server is running
- Verify network connection

**No data appearing:**
- Wait for monitor to send first update
- Check LMU is running (if using real data)
- Check monitor console for errors

**Stale data warning:**
- Monitor may have disconnected
- Check monitor console
- Dashboard will auto-reconnect

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.
```

## Success Criteria

- [x] README.md created with quick start
- [x] Installation guide written
- [x] Usage guide with screenshots
- [ ] Deployment guide complete
- [ ] API reference documented
- [ ] Troubleshooting guide created
- [ ] Architecture diagram added
- [ ] All documentation reviewed for accuracy

## Documentation Standards

**Style:**
- Clear, concise language
- Step-by-step instructions
- Code examples for all commands
- Screenshots where helpful
- Links between related docs

**Format:**
- Markdown format
- GitHub-flavored markdown
- Consistent heading levels
- Code blocks with syntax highlighting
- Tables for comparisons

**Content:**
- Assume reader is developer
- Provide context before instructions
- Include error messages and solutions
- Link to related documentation
- Keep up-to-date with code changes

## Related Files

- `README.md` - Main documentation
- `docs/INSTALLATION.md` - Installation guide
- `docs/USAGE.md` - User guide
- `docs/DEPLOYMENT.md` - Deployment options
- `docs/API.md` - WebSocket API reference
- `docs/TROUBLESHOOTING.md` - Problem solving

## References

- RACE_DASHBOARD_PLAN.md - Lines 326-365 (monitor README)
- RACE_DASHBOARD_PLAN.md - Lines 1058-1112 (server README)
- Good README examples: https://github.com/matiassingers/awesome-readme
