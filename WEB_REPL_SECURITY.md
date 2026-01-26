# Web REPL Security Guide

## Overview

The Syntari Web REPL implements comprehensive security measures to protect against abuse, resource exhaustion, and malicious code execution. This guide covers all security features and best practices.

## Security Features

### 1. Rate Limiting

**Purpose:** Prevent abuse and resource exhaustion through request throttling

**Features:**
- Per-IP rate limiting (requests/minute and requests/hour)
- Code length limits
- Execution time monitoring
- Automatic banning after repeated violations
- Exponential backoff for persistent violators

**Default Limits:**
```python
requests_per_minute: 30
requests_per_hour: 500
max_code_length: 10,000 characters
max_execution_time: 5.0 seconds
ban_threshold: 10 violations
ban_duration: 300 seconds (5 minutes)
```

**Configuration:**
```python
from web.security import RateLimiter, RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=30,
    requests_per_hour=500,
    max_code_length=10000,
    max_execution_time=5.0,
    ban_threshold=10,
    ban_duration=300,
)

rate_limiter = RateLimiter(config)
```

**Usage:**
```python
# Check if request is allowed
allowed, reason = rate_limiter.check_rate_limit(ip_address)
if not allowed:
    return error_response(reason)

# Check code length
allowed, reason = rate_limiter.check_code_length(code, ip_address)

# Record execution time
rate_limiter.record_execution_time(ip_address, execution_time, code_length, success)

# Get client statistics
stats = rate_limiter.get_client_stats(ip_address)
```

### 2. Session Management

**Purpose:** Secure, stateful user sessions with timeout and cleanup

**Features:**
- Secure token generation (UUID4 + 256-bit random token)
- Token hashing with SHA-256
- Session timeout (default: 1 hour)
- Per-IP session limits
- Automatic cleanup of expired sessions
- IP address validation

**Default Configuration:**
```python
session_timeout: 3600 seconds (1 hour)
max_sessions_per_ip: 5
session_cleanup_interval: 300 seconds (5 minutes)
```

**Configuration:**
```python
from web.security import SessionManager, SessionConfig

config = SessionConfig(
    session_timeout=3600,
    max_sessions_per_ip=5,
    session_cleanup_interval=300,
)

session_manager = SessionManager(config)
```

**Usage:**
```python
# Create new session
result = session_manager.create_session(ip_address)
if result:
    session_id, session_token = result
    # Store token securely (HTTPS only, httpOnly cookie)

# Validate session
valid = session_manager.validate_session(session_id, session_token, ip_address)

# Remove session
session_manager.remove_session(session_id, session_token)

# Get statistics
stats = session_manager.get_stats()
```

**Security Best Practices:**
- Always transmit tokens over HTTPS
- Store tokens in httpOnly cookies (not localStorage)
- Never log session tokens
- Rotate tokens after privilege changes
- Clear tokens on logout

### 3. Resource Monitoring

**Purpose:** Track and limit resource consumption per client

**Features:**
- Execution time tracking
- Memory usage monitoring
- Windowed metrics (configurable time window)
- Per-client and per-session tracking

**Usage:**
```python
from web.security import ResourceMonitor

monitor = ResourceMonitor()

# Record execution
monitor.record_execution(identifier, execution_time, memory_mb)

# Get metrics (default: 60 second window)
metrics = monitor.get_metrics(identifier, window=60)
# Returns: count, avg_execution_time, max_execution_time, total_memory_mb
```

### 4. Input Sanitization

**Purpose:** Prevent XSS and injection attacks

**Features:**
- HTML entity encoding
- Control character removal (preserves newlines/tabs)
- Length limiting
- Output truncation for large results

**Usage:**
```python
from web.security import sanitize_output

# Sanitize output for display
safe_output = sanitize_output(untrusted_text, max_length=10000)
```

**Protected Against:**
- XSS (Cross-Site Scripting)
- HTML injection
- Control character injection
- Output flooding

### 5. Code Safety Validation

**Purpose:** Block potentially dangerous operations

**Features:**
- Pattern-based detection of dangerous functions
- Blacklist of prohibited operations
- Early rejection before execution

**Blocked Patterns:**
```python
__import__
eval(
exec(
compile(
open(
file(
__builtins__
system(
popen(
```

**Usage:**
```python
from web.security import validate_code_safety

safe, reason = validate_code_safety(code)
if not safe:
    return error_response(reason)
```

**Note:** This is a basic check. The VM's built-in security features provide the main protection layer.

### 6. CORS Configuration

**Purpose:** Control which origins can access the Web REPL

**Configuration:**
```python
# In app.py
import os

cors_origin = os.environ.get("SYNTARI_CORS_ORIGIN", "http://localhost:8080")
```

**Environment Variables:**
```bash
# Development (default)
SYNTARI_CORS_ORIGIN=http://localhost:8080

# Production (specific domain)
SYNTARI_CORS_ORIGIN=https://syntari.example.com

# Multiple origins (configure in code)
SYNTARI_CORS_ORIGINS=https://app1.example.com,https://app2.example.com
```

**Production Configuration:**
```python
# For production, use specific origins
cors = aiohttp_cors.setup(
    app,
    defaults={
        "https://syntari.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    },
)
```

## API Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.4.0",
  "security": {
    "rate_limiting": "enabled",
    "session_management": "enabled",
    "resource_monitoring": "enabled"
  }
}
```

### Statistics (Admin Only)

```
GET /stats
Authorization: Bearer admin-token-change-me
```

**Response:**
```json
{
  "rate_limiter": {
    "total_clients": 42,
    "active_clients": 15,
    "banned_clients": 2
  },
  "sessions": {
    "total_sessions": 38,
    "unique_ips": 35,
    "avg_requests_per_session": 12.5
  },
  "active_connections": 15,
  "resource_metrics": {
    "192.168.1.100": {
      "count": 10,
      "avg_execution_time": 0.25,
      "max_execution_time": 1.2,
      "total_memory_mb": 50
    }
  }
}
```

### Client Statistics

```
GET /client-stats
```

**Response:**
```json
{
  "rate_limit": {
    "ip_address": "192.168.1.100",
    "total_requests": 125,
    "total_violations": 2,
    "current_violations": 0,
    "is_banned": false,
    "requests_last_minute": 5,
    "requests_last_hour": 78
  },
  "resources": {
    "count": 78,
    "avg_execution_time": 0.35,
    "max_execution_time": 2.1,
    "total_memory_mb": 250
  }
}
```

### WebSocket Protocol

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
```

**Execute Code:**
```json
{
  "command": "execute",
  "code": "let x = 5\nprint(x)"
}
```

**Response:**
```json
{
  "type": "result",
  "data": {
    "success": true,
    "output": "5\n",
    "error": null,
    "result": null,
    "execution_time": 0.012
  }
}
```

**Error Response:**
```json
{
  "type": "error",
  "data": {
    "error": "Rate limit: 30 requests/minute"
  }
}
```

## Deployment Recommendations

### 1. Use HTTPS

**Always use HTTPS in production:**
```bash
# Use a reverse proxy like Nginx
server {
    listen 443 ssl http2;
    server_name syntari.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Configure Firewall

**Allow only necessary traffic:**
```bash
# UFW example
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp  # For HTTPS redirect
sudo ufw deny 8080/tcp  # Block direct access to app
```

### 3. Use Environment Variables

**Store secrets in environment:**
```bash
# .env file (never commit this!)
SYNTARI_ADMIN_TOKEN=your-secure-token-here
SYNTARI_CORS_ORIGIN=https://syntari.example.com
SYNTARI_SESSION_SECRET=your-session-secret-here
```

**Load in app:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_TOKEN = os.environ.get("SYNTARI_ADMIN_TOKEN")
```

### 4. Rate Limit Configuration

**Adjust for production workload:**
```python
# Production configuration
config = RateLimitConfig(
    requests_per_minute=60,  # Higher for authenticated users
    requests_per_hour=1000,
    max_code_length=5000,  # Stricter limits
    max_execution_time=3.0,  # Faster timeout
    ban_threshold=5,  # Less tolerant
    ban_duration=600,  # Longer ban (10 minutes)
)
```

### 5. Monitoring and Logging

**Set up monitoring:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('syntari_web.log'),
        logging.StreamHandler()
    ]
)

# Log security events
logger = logging.getLogger('syntari.security')

@app.middleware
async def security_logging(request, handler):
    start = time.time()
    response = await handler(request)
    duration = time.time() - start
    
    logger.info(f"{request.remote} - {request.method} {request.path} - {response.status} - {duration:.3f}s")
    
    return response
```

### 6. Database for Session Storage

**For production, use Redis:**
```python
import aioredis

class RedisSessionManager(SessionManager):
    def __init__(self, redis_url, config=None):
        super().__init__(config)
        self.redis = aioredis.from_url(redis_url)
    
    async def create_session(self, ip_address):
        session_id, token = super().create_session(ip_address)
        await self.redis.setex(
            f"session:{session_id}",
            self.config.session_timeout,
            token
        )
        return session_id, token
```

## Security Incident Response

### Handling Abuse

**1. Identify the attacker:**
```python
# Check client stats
stats = rate_limiter.get_client_stats(suspicious_ip)
print(f"Violations: {stats['total_violations']}")
print(f"Banned: {stats['is_banned']}")
```

**2. Manual ban:**
```python
# Manually ban an IP
client = rate_limiter.clients[suspicious_ip]
client.banned_until = time.time() + 86400  # Ban for 24 hours
```

**3. Clear session:**
```python
# Terminate all sessions from IP
for session_key in list(session_manager.sessions.keys()):
    session = session_manager.sessions[session_key]
    if session.ip_address == suspicious_ip:
        session_manager._remove_session(session_key)
```

### Reviewing Logs

**Check for patterns:**
```bash
# Failed executions
grep "Runtime error" syntari_web.log | wc -l

# Rate limit violations
grep "Rate limit" syntari_web.log

# Banned IPs
grep "Temporarily banned" syntari_web.log | cut -d' ' -f3 | sort | uniq -c
```

## Testing Security

### Rate Limiting Test

```bash
# Test rate limits with curl
for i in {1..35}; do
  curl -X POST http://localhost:8080/ws \
    -H "Content-Type: application/json" \
    -d '{"command":"execute","code":"print(1)"}' &
done
wait

# Should see rate limit errors after request 30
```

### Code Safety Test

```python
# Should be blocked
dangerous_codes = [
    "__import__('os').system('ls')",
    "eval('malicious code')",
    "open('/etc/passwd').read()",
]

for code in dangerous_codes:
    safe, reason = validate_code_safety(code)
    assert not safe
```

### Session Test

```python
# Test session timeout
session_id, token = session_manager.create_session("192.168.1.1")
assert session_manager.validate_session(session_id, token, "192.168.1.1")

time.sleep(config.session_timeout + 1)

assert not session_manager.validate_session(session_id, token, "192.168.1.1")
```

## Performance Considerations

### Rate Limiter

- **Memory Usage:** ~1KB per client
- **CPU Impact:** Minimal (O(1) operations)
- **Cleanup:** Automatic (removes old request records)

### Session Manager

- **Memory Usage:** ~500 bytes per session
- **CPU Impact:** Minimal (hash lookups)
- **Cleanup:** Periodic (configurable interval)

### Resource Monitor

- **Memory Usage:** ~100 bytes per recorded execution
- **CPU Impact:** Minimal
- **History:** Limited to last 100 executions per client

## Compliance and Standards

### OWASP Top 10 Coverage

✅ **A01: Broken Access Control** - Session management, IP validation
✅ **A02: Cryptographic Failures** - Token hashing, HTTPS
✅ **A03: Injection** - Code safety validation, input sanitization
✅ **A04: Insecure Design** - Rate limiting, resource limits
✅ **A05: Security Misconfiguration** - Secure defaults, environment variables
✅ **A07: Identification and Authentication Failures** - Session tokens, timeouts
✅ **A10: Server-Side Request Forgery** - Restricted network access

### Security Headers

**Recommended headers for production:**
```python
@app.middleware
async def security_headers(request, handler):
    response = await handler(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

## Troubleshooting

### Rate Limit False Positives

**Problem:** Legitimate users hitting rate limits

**Solution:**
```python
# Increase limits for authenticated users
if user.is_authenticated:
    config = RateLimitConfig(requests_per_minute=120)
else:
    config = RateLimitConfig(requests_per_minute=30)
```

### Session Expiring Too Quickly

**Problem:** Users complaining about frequent logouts

**Solution:**
```python
# Increase session timeout
config = SessionConfig(session_timeout=7200)  # 2 hours

# Or implement session refresh
async def refresh_session(session_id, token, ip):
    session = session_manager.get_session(session_id, token)
    if session:
        session.last_activity = time.time()
```

### High Memory Usage

**Problem:** Server running out of memory

**Solution:**
```python
# Reduce history sizes
rate_limiter.config.requests_per_hour = 100  # Lower limit
session_manager.config.max_sessions_per_ip = 3

# More aggressive cleanup
session_manager.config.session_cleanup_interval = 60  # 1 minute
```

## Changelog

### v0.4.0 (Current)
- ✅ Rate limiting with per-minute and per-hour limits
- ✅ Session management with secure tokens
- ✅ Resource monitoring
- ✅ Input sanitization
- ✅ Code safety validation
- ✅ CORS configuration
- ✅ Statistics endpoints

### v0.5.0 (Planned)
- [ ] Redis-backed session storage
- [ ] JWT authentication
- [ ] OAuth2 integration
- [ ] Advanced DDoS protection
- [ ] IP whitelist/blacklist
- [ ] Audit logging

## Support

For security issues, contact: security@deuos.io

For general questions: legal@deuos.io

---

**Last Updated:** January 26, 2026
**Version:** 0.4.0
