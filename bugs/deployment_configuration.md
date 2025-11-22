# Deployment Configuration

**Date Created:** 2025-11-22
**Priority:** Medium
**Component:** Dashboard Server - Deployment
**Phase:** Phase 2 Polish

## Description

Set up deployment configurations and documentation for both local network and cloud hosting options to make the dashboard accessible to team members.

## Requirements

### Must Have - Local Network Deployment
1. Run server on driver's PC (localhost)
2. Accessible via LAN IP address
3. Configure firewall rules (port 5000)
4. Instructions for finding local IP
5. Test access from mobile devices on same network

### Must Have - Cloud Deployment Preparation
1. Production-ready server configuration
2. Environment variable management
3. Gunicorn/production WSGI server setup
4. HTTPS support (future)
5. Deployment documentation

### Nice to Have
1. Docker containerization
2. Heroku deployment
3. Railway/Render deployment
4. Auto-deployment via CI/CD
5. Health check endpoint
6. Monitoring/logging service

## Technical Details

### Local Network Deployment

**Find Local IP (Windows):**
```cmd
ipconfig
# Look for IPv4 Address: 192.168.x.x
```

**Find Local IP (macOS/Linux):**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# or
hostname -I
```

**Start Server:**
```bash
python run.py
# Server runs on: http://0.0.0.0:5000
# Accessible via: http://192.168.x.x:5000/dashboard/<session-id>
```

**Firewall Configuration:**

Windows:
```cmd
# Allow incoming on port 5000
netsh advfirewall firewall add rule name="1Lap Dashboard" dir=in action=allow protocol=TCP localport=5000
```

Linux:
```bash
sudo ufw allow 5000/tcp
```

macOS:
```bash
# System Preferences → Security & Privacy → Firewall → Firewall Options
# Add Python and allow incoming connections
```

### Production Configuration

**File:** `.env.example`
```bash
# Server Configuration
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
HOST=0.0.0.0
PORT=5000

# CORS (production)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/1lap/dashboard.log
```

**Gunicorn Configuration:**

**File:** `gunicorn_config.py`
```python
"""Gunicorn configuration for production"""

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = 1  # Must be 1 for WebSocket
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Process naming
proc_name = "1lap-dashboard"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

**Start with Gunicorn:**
```bash
gunicorn -c gunicorn_config.py run:app
```

### Docker Deployment

**File:** `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "run:app"]
```

**File:** `docker-compose.yml`
```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/var/log/1lap
    restart: unless-stopped
```

**Run with Docker:**
```bash
# Build
docker build -t 1lap-dashboard .

# Run
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key 1lap-dashboard

# Or with docker-compose
docker-compose up -d
```

### Cloud Deployment - Heroku

**File:** `Procfile`
```
web: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app
```

**File:** `runtime.txt`
```
python-3.11.0
```

**Deploy to Heroku:**
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create 1lap-dashboard

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Open
heroku open
```

**Custom Domain (Heroku):**
```bash
# Add domain
heroku domains:add dashboard.1lap.io

# Get DNS target
heroku domains

# Update DNS:
# Add CNAME: dashboard.1lap.io → your-app.herokuapp.com
```

### Cloud Deployment - Railway

**Deploy Button:**
```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
```

**railway.json:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Manual Deploy:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### Health Check Endpoint

**File:** `app/main.py`
```python
@current_app.route('/health')
def health():
    """Health check endpoint for load balancers"""
    return {
        'status': 'ok',
        'version': '1.0.0',
        'active_sessions': len(session_mgr.get_active_sessions())
    }, 200
```

## Success Criteria

### Local Network
- [x] Server starts on 0.0.0.0:5000
- [x] Accessible via local IP
- [x] Mobile devices can connect on LAN
- [x] Firewall configured correctly
- [ ] Documentation complete

### Production
- [x] Gunicorn configuration created
- [x] Environment variables documented
- [x] Docker setup (optional)
- [ ] Cloud deployment tested (Heroku/Railway)
- [ ] HTTPS configured (future)
- [ ] Health check endpoint added

## Documentation

**File:** `DEPLOYMENT.md`

Create comprehensive deployment guide with:
1. Local network setup (step-by-step)
2. Cloud deployment options (Heroku, Railway, Render)
3. Environment variables
4. Firewall configuration
5. Troubleshooting common issues
6. Security best practices

## Testing Deployment

**Local Network:**
```bash
# 1. Start server
python run.py

# 2. Find local IP
ipconfig  # Windows
ifconfig  # macOS/Linux

# 3. Test from same network
# Phone browser: http://192.168.x.x:5000/dashboard/test-session-id
# Should see dashboard UI
```

**Production:**
```bash
# 1. Start with gunicorn
gunicorn -c gunicorn_config.py run:app

# 2. Test health endpoint
curl http://localhost:5000/health

# 3. Test WebSocket
# Use browser console or test client
```

**Docker:**
```bash
# 1. Build
docker build -t 1lap-dashboard .

# 2. Run
docker run -p 5000:5000 1lap-dashboard

# 3. Test
curl http://localhost:5000/health
```

## Security Checklist

**Production Deployment:**
- [ ] Set strong SECRET_KEY (random, not in version control)
- [ ] Disable DEBUG mode (DEBUG=False)
- [ ] Restrict CORS origins (not "*")
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable logging
- [ ] Regular security updates
- [ ] Monitor for suspicious activity

## Performance Optimization

**Gunicorn Workers:**
```python
# WebSocket requires single worker
workers = 1

# For higher throughput, use threads
workers = 1
threads = 4  # Handle 4 concurrent connections
```

**Nginx Reverse Proxy (Optional):**
```nginx
upstream dashboard {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name dashboard.1lap.io;

    location / {
        proxy_pass http://dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

**Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/1lap/dashboard.log'),
        logging.StreamHandler()
    ]
)
```

**Metrics (Future):**
- Active sessions count
- Total connections
- Messages per second
- Error rate
- Response time

## Related Files

- `run.py` - Development server
- `gunicorn_config.py` - Production server config
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Container orchestration
- `Procfile` - Heroku configuration
- `.env.example` - Environment variables template
- `DEPLOYMENT.md` - Deployment documentation

## Cost Estimates

**Local Network:** $0 (runs on driver's PC)

**Cloud Hosting:**
- Heroku: $0-7/month (free tier or Hobby)
- Railway: $0-5/month (free tier or Pro)
- Render: $0-7/month (free tier or Starter)
- DigitalOcean: $5/month (smallest droplet)
- AWS/GCP/Azure: ~$10-20/month (varies)

**Recommendation:** Start with local network, upgrade to cloud if needed for remote team members.

## References

- RACE_DASHBOARD_PLAN.md - Lines 1381-1471 (Deployment options)
- Gunicorn docs: https://docs.gunicorn.org/
- Heroku Python: https://devcenter.heroku.com/articles/getting-started-with-python
- Railway docs: https://docs.railway.app/
- Docker docs: https://docs.docker.com/
