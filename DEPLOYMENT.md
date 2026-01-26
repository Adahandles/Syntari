# Syntari Production Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)
11. [CI/CD Pipeline](#cicd-pipeline)

---

## Overview

This guide covers deploying Syntari v0.4 to production environments including:
- Standalone interpreter
- Web REPL server
- LSP server for IDE integration
- Package registry

---

## Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing (`pytest tests/` - should show 473+ tests passing)
- [ ] No security vulnerabilities (`make security`)
- [ ] Code formatted (`make format-check`)
- [ ] Linting passed (`make lint`)
- [ ] Type checking passed (`mypy src/`)
- [ ] Documentation up to date

### Security

- [ ] Security audit completed
- [ ] Rate limiting configured
- [ ] Session management enabled
- [ ] Input validation in place
- [ ] Secrets rotated
- [ ] SSL/TLS certificates ready

### Infrastructure

- [ ] Server provisioned
- [ ] Database configured (if needed)
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] DNS records configured

---

## System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **Python**: 3.8+
- **Memory**: 512 MB RAM
- **Disk**: 100 MB free space
- **CPU**: 1 core

### Recommended for Production

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10+
- **Memory**: 2 GB RAM
- **Disk**: 1 GB free space (with logs)
- **CPU**: 2+ cores
- **Network**: 100 Mbps+

### Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Python packages
pip install -r requirements.txt
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Adahandles/Syntari.git
cd Syntari
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Syntari

```bash
# Production install (no dev dependencies)
pip install -e .

# Or with web server support
pip install -e ".[web]"
```

### 4. Verify Installation

```bash
# Check version
syntari --version

# Run tests
pytest tests/ -q

# Run example
syntari examples/hello_world.syn
```

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Application
SYNTARI_ENV=production
SYNTARI_LOG_LEVEL=INFO
SYNTARI_LOG_FILE=/var/log/syntari/syntari.log

# Web REPL (if using)
SYNTARI_WEB_HOST=0.0.0.0
SYNTARI_WEB_PORT=8080
SYNTARI_WEB_CORS_ORIGINS=https://yourdomain.com

# Security
SYNTARI_RATE_LIMIT_REQUESTS=30
SYNTARI_RATE_LIMIT_PERIOD=60
SYNTARI_SESSION_TIMEOUT=3600
SYNTARI_MAX_EXECUTION_TIME=30

# Monitoring
SYNTARI_METRICS_ENABLED=true
SYNTARI_METRICS_PORT=9090
```

### Logging Configuration

```python
# config/logging.py
from src.core.logging import configure_logging, LogLevel, LogFormat

configure_logging(
    level=LogLevel.INFO,
    format_type=LogFormat.JSON,
    log_file="/var/log/syntari/syntari.log",
    max_bytes=100 * 1024 * 1024,  # 100MB
    backup_count=10,
)
```

### Web REPL Configuration

```python
# config/web_repl.py
WEB_REPL_CONFIG = {
    "host": "0.0.0.0",
    "port": 8080,
    "cors_origins": ["https://yourdomain.com"],
    "rate_limiting": {
        "enabled": True,
        "per_minute": 30,
        "per_hour": 500,
    },
    "security": {
        "session_timeout": 3600,
        "max_execution_time": 30,
        "max_memory_mb": 100,
    },
}
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Deny direct access to app port (use reverse proxy)
sudo ufw deny 8080/tcp
```

### 2. Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/syntari
server {
    listen 80;
    server_name syntari.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name syntari.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/syntari.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/syntari.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=syntari:10m rate=10r/s;
    limit_req zone=syntari burst=20 nodelay;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/syntari /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL/TLS (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d syntari.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 4. System User

```bash
# Create dedicated user
sudo useradd -r -s /bin/false syntari

# Set ownership
sudo chown -R syntari:syntari /opt/syntari
sudo chmod 750 /opt/syntari
```

---

## Monitoring

### 1. Application Metrics

Use built-in performance logger:

```python
from src.core.logging import get_logger, PerformanceLogger

logger = get_logger()
perf = PerformanceLogger(logger)

# Log execution time
perf.log_execution_time("parse_file", 123.45)

# Get stats
stats = perf.get_stats("parse_file")
print(stats)  # {count, total_ms, avg_ms, min_ms, max_ms}
```

### 2. System Monitoring (Prometheus + Grafana)

**Prometheus Configuration** (`prometheus.yml`):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'syntari'
    static_configs:
      - targets: ['localhost:9090']
```

**Grafana Dashboard**:
- Request rate (requests/sec)
- Error rate (errors/sec)
- Response time (p50, p95, p99)
- Memory usage
- CPU usage
- Active sessions

### 3. Log Monitoring (ELK Stack)

**Filebeat Configuration** (`filebeat.yml`):
```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/syntari/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "syntari-%{+yyyy.MM.dd}"
```

### 4. Health Checks

Create health check endpoint:

```python
# web/health.py
from aiohttp import web

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "version": "0.4.0",
        "timestamp": datetime.now().isoformat(),
    })

# Add to routes
app.router.add_get("/health", health_check)
```

Monitor with:
```bash
# Simple check
curl https://syntari.yourdomain.com/health

# Or use monitoring tool
# Uptime Robot, Pingdom, etc.
```

---

## Backup & Recovery

### 1. Backup Strategy

**Daily Backups**:
```bash
#!/bin/bash
# /opt/syntari/scripts/backup.sh

BACKUP_DIR="/var/backups/syntari"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application
tar -czf "$BACKUP_DIR/syntari_app_$DATE.tar.gz" /opt/syntari

# Backup logs
tar -czf "$BACKUP_DIR/syntari_logs_$DATE.tar.gz" /var/log/syntari

# Backup configuration
tar -czf "$BACKUP_DIR/syntari_config_$DATE.tar.gz" /etc/syntari

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "syntari_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job**:
```bash
# Add to crontab
sudo crontab -e

# Daily at 2 AM
0 2 * * * /opt/syntari/scripts/backup.sh >> /var/log/syntari/backup.log 2>&1
```

### 2. Restore Procedure

```bash
#!/bin/bash
# Restore from backup

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Stop service
sudo systemctl stop syntari

# Restore
tar -xzf "$BACKUP_FILE" -C /

# Restart service
sudo systemctl start syntari

echo "Restore completed"
```

### 3. Disaster Recovery

**Recovery Time Objective (RTO)**: < 1 hour  
**Recovery Point Objective (RPO)**: < 24 hours

**Steps**:
1. Provision new server
2. Install Python and dependencies
3. Restore from latest backup
4. Update DNS records
5. Verify functionality
6. Monitor for issues

---

## Performance Tuning

### 1. Python Optimization

```bash
# Use optimized Python
python3 -O -m syntari.main

# Or in production
PYTHONOPTIMIZE=2 python3 -m syntari.main
```

### 2. Gunicorn (Web REPL)

```bash
# Install
pip install gunicorn

# Run with multiple workers
gunicorn web.app:app \
    --workers 4 \
    --worker-class aiohttp.GunicornWebWorker \
    --bind 0.0.0.0:8080 \
    --timeout 60 \
    --access-logfile /var/log/syntari/access.log \
    --error-logfile /var/log/syntari/error.log \
    --log-level info
```

### 3. System Limits

```bash
# /etc/security/limits.conf
syntari soft nofile 65536
syntari hard nofile 65536
syntari soft nproc 4096
syntari hard nproc 4096
```

### 4. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def parse_cached(source_code):
    """Cache parsed AST"""
    return parse(source_code)
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Check logs**:
```bash
sudo journalctl -u syntari -f
tail -f /var/log/syntari/syntari.log
```

**Common causes**:
- Port already in use
- Permission denied
- Missing dependencies
- Configuration error

#### 2. High Memory Usage

**Diagnosis**:
```bash
# Check process memory
ps aux | grep syntari

# Monitor in real-time
top -p $(pgrep -f syntari)
```

**Solutions**:
- Reduce worker count
- Enable memory limits
- Add swap space
- Upgrade hardware

#### 3. Slow Response Times

**Diagnosis**:
```bash
# Check request latency
curl -w "@curl-format.txt" -o /dev/null -s https://syntari.yourdomain.com/
```

**Solutions**:
- Enable caching
- Optimize code (profile with `--profile`)
- Add more workers
- Use CDN

#### 4. Rate Limiting Issues

**Check rate limiter status**:
```bash
curl https://syntari.yourdomain.com/admin/stats
```

**Adjust limits** in configuration if needed.

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Security check
        run: |
          pip install bandit safety
          bandit -r src/
          safety check
      
      - name: Lint
        run: |
          pip install flake8 mypy black
          flake8 src/ tests/
          mypy src/
          black --check src/ tests/
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/syntari
            git pull origin main
            source venv/bin/activate
            pip install -e .
            sudo systemctl restart syntari
```

### Manual Deployment

```bash
# 1. SSH to server
ssh user@server

# 2. Update code
cd /opt/syntari
git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -e .

# 5. Run tests
pytest tests/ -q

# 6. Restart service
sudo systemctl restart syntari

# 7. Check status
sudo systemctl status syntari

# 8. Monitor logs
tail -f /var/log/syntari/syntari.log
```

---

## Systemd Service

Create `/etc/systemd/system/syntari.service`:

```ini
[Unit]
Description=Syntari Programming Language Service
After=network.target

[Service]
Type=simple
User=syntari
Group=syntari
WorkingDirectory=/opt/syntari
Environment="PATH=/opt/syntari/venv/bin"
Environment="SYNTARI_ENV=production"
ExecStart=/opt/syntari/venv/bin/python3 -m web.app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/syntari

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable syntari
sudo systemctl start syntari
sudo systemctl status syntari
```

---

## Production Checklist

Before going live:

### Testing
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Security audit completed

### Configuration
- [ ] Environment variables set
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backups configured

### Security
- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Input validation enabled
- [ ] Secrets rotated

### Documentation
- [ ] Deployment guide reviewed
- [ ] Runbook created
- [ ] Contact information updated
- [ ] Incident response plan

### Launch
- [ ] DNS updated
- [ ] Service started
- [ ] Health check passing
- [ ] Monitoring active
- [ ] Team notified

---

## Support

For production support:
- **Email**: legal@deuos.io
- **GitHub Issues**: https://github.com/Adahandles/Syntari/issues
- **Documentation**: https://github.com/Adahandles/Syntari

---

**Version**: Syntari v0.4  
**Last Updated**: December 2024  
**Copyright © 2024 DeuOS, LLC**
