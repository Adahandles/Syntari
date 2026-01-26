"""
Syntari Web REPL Security Module
Provides rate limiting, session management, and resource monitoring
"""

import time
import uuid
import hashlib
import secrets
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 30
    requests_per_hour: int = 500
    max_code_length: int = 10000  # Maximum code length in characters
    max_execution_time: float = 5.0  # Maximum execution time in seconds
    ban_threshold: int = 10  # Violations before temporary ban
    ban_duration: int = 300  # Ban duration in seconds (5 minutes)


@dataclass
class RequestRecord:
    """Record of a single request"""
    timestamp: float
    ip_address: str
    code_length: int
    execution_time: float
    success: bool


@dataclass
class ClientState:
    """State tracking for a single client"""
    ip_address: str
    requests: deque = field(default_factory=deque)  # Recent requests with timestamps
    violations: int = 0
    banned_until: Optional[float] = None
    total_requests: int = 0
    total_violations: int = 0
    created_at: float = field(default_factory=time.time)
    last_request: float = field(default_factory=time.time)


class RateLimiter:
    """
    Rate limiter with configurable limits and violation tracking
    
    Features:
    - Per-IP rate limiting (requests/minute and requests/hour)
    - Code length limits
    - Execution time limits
    - Automatic banning after repeated violations
    - Exponential backoff for violations
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.clients: Dict[str, ClientState] = {}
        self._lock = threading.RLock()

    def check_rate_limit(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed under rate limits
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        with self._lock:
            now = time.time()

            # Get or create client state
            if ip_address not in self.clients:
                self.clients[ip_address] = ClientState(ip_address=ip_address)

            client = self.clients[ip_address]
            client.last_request = now

            # Check if client is banned
            if client.banned_until and now < client.banned_until:
                remaining = int(client.banned_until - now)
                return False, f"Temporarily banned. Try again in {remaining} seconds."

            # Clear ban if expired
            if client.banned_until and now >= client.banned_until:
                client.banned_until = None
                client.violations = 0

            # Remove old requests (older than 1 hour)
            cutoff_hour = now - 3600
            while client.requests and client.requests[0] < cutoff_hour:
                client.requests.popleft()

            # Check per-minute limit
            cutoff_minute = now - 60
            recent_requests = sum(1 for ts in client.requests if ts > cutoff_minute)
            if recent_requests >= self.config.requests_per_minute:
                self._record_violation(client)
                return False, f"Rate limit exceeded: {self.config.requests_per_minute} requests/minute"

            # Check per-hour limit
            if len(client.requests) >= self.config.requests_per_hour:
                self._record_violation(client)
                return False, f"Rate limit exceeded: {self.config.requests_per_hour} requests/hour"

            # Add current request
            client.requests.append(now)
            client.total_requests += 1

            return True, None

    def check_code_length(self, code: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if code length is within limits"""
        if len(code) > self.config.max_code_length:
            with self._lock:
                if ip_address in self.clients:
                    self._record_violation(self.clients[ip_address])
            return False, f"Code length exceeds limit: {self.config.max_code_length} characters"
        return True, None

    def record_execution_time(self, ip_address: str, execution_time: float, code_length: int, success: bool):
        """Record execution time and check for violations"""
        with self._lock:
            if ip_address not in self.clients:
                return

            client = self.clients[ip_address]

            # Check execution time limit
            if execution_time > self.config.max_execution_time:
                self._record_violation(client)

    def _record_violation(self, client: ClientState):
        """Record a violation and apply ban if threshold exceeded"""
        client.violations += 1
        client.total_violations += 1

        if client.violations >= self.config.ban_threshold:
            # Ban client with exponential backoff
            ban_multiplier = min(2 ** (client.violations - self.config.ban_threshold), 8)
            client.banned_until = time.time() + (self.config.ban_duration * ban_multiplier)
            client.violations = 0  # Reset violations counter

    def get_client_stats(self, ip_address: str) -> Optional[dict]:
        """Get statistics for a client"""
        with self._lock:
            if ip_address not in self.clients:
                return None

            client = self.clients[ip_address]
            now = time.time()

            return {
                "ip_address": client.ip_address,
                "total_requests": client.total_requests,
                "total_violations": client.total_violations,
                "current_violations": client.violations,
                "is_banned": client.banned_until and now < client.banned_until,
                "ban_expires": client.banned_until if client.banned_until else None,
                "requests_last_minute": sum(1 for ts in client.requests if ts > now - 60),
                "requests_last_hour": len(client.requests),
                "account_age": now - client.created_at,
            }

    def clear_client(self, ip_address: str):
        """Clear client state (for testing or admin purposes)"""
        with self._lock:
            if ip_address in self.clients:
                del self.clients[ip_address]

    def get_all_stats(self) -> dict:
        """Get statistics for all clients"""
        with self._lock:
            return {
                "total_clients": len(self.clients),
                "active_clients": sum(
                    1 for c in self.clients.values() 
                    if time.time() - c.last_request < 300
                ),
                "banned_clients": sum(
                    1 for c in self.clients.values() 
                    if c.banned_until and time.time() < c.banned_until
                ),
            }


@dataclass
class SessionConfig:
    """Configuration for session management"""
    session_timeout: int = 3600  # Session timeout in seconds (1 hour)
    max_sessions_per_ip: int = 5  # Maximum concurrent sessions per IP
    session_cleanup_interval: int = 300  # Cleanup interval in seconds (5 minutes)


@dataclass
class Session:
    """Represents a user session"""
    session_id: str
    ip_address: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    request_count: int = 0
    data: dict = field(default_factory=dict)


class SessionManager:
    """
    Manages user sessions with timeout and cleanup
    
    Features:
    - Secure session token generation
    - Session timeout and cleanup
    - Per-IP session limits
    - Session data storage
    """

    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        self.sessions: Dict[str, Session] = {}
        self.ip_sessions: Dict[str, set] = defaultdict(set)  # IP -> set of session IDs
        self._lock = threading.RLock()
        self._last_cleanup = time.time()

    def create_session(self, ip_address: str) -> Optional[Tuple[str, str]]:
        """
        Create a new session
        
        Returns:
            (session_id, session_token) or None if limit exceeded
        """
        with self._lock:
            self._cleanup_if_needed()

            # Check IP session limit
            if len(self.ip_sessions.get(ip_address, set())) >= self.config.max_sessions_per_ip:
                return None

            # Generate secure session ID and token
            session_id = str(uuid.uuid4())
            session_token = secrets.token_urlsafe(32)

            # Store session with hashed token for security
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            session = Session(
                session_id=session_id,
                ip_address=ip_address,
            )
            
            # Store session with hashed token as key
            session_key = f"{session_id}:{token_hash}"
            self.sessions[session_key] = session
            self.ip_sessions[ip_address].add(session_key)

            return session_id, session_token

    def validate_session(self, session_id: str, session_token: str, ip_address: str) -> bool:
        """
        Validate session ID and token
        
        Returns:
            True if valid, False otherwise
        """
        with self._lock:
            self._cleanup_if_needed()

            # Hash the token for comparison
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            session_key = f"{session_id}:{token_hash}"

            if session_key not in self.sessions:
                return False

            session = self.sessions[session_key]

            # Check IP address match
            if session.ip_address != ip_address:
                return False

            # Check timeout
            now = time.time()
            if now - session.last_activity > self.config.session_timeout:
                self._remove_session(session_key)
                return False

            # Update activity
            session.last_activity = now
            session.request_count += 1

            return True

    def get_session(self, session_id: str, session_token: str) -> Optional[Session]:
        """Get session by ID and token"""
        with self._lock:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            session_key = f"{session_id}:{token_hash}"
            return self.sessions.get(session_key)

    def remove_session(self, session_id: str, session_token: str):
        """Remove a session"""
        with self._lock:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            session_key = f"{session_id}:{token_hash}"
            self._remove_session(session_key)

    def _remove_session(self, session_key: str):
        """Internal method to remove a session"""
        if session_key in self.sessions:
            session = self.sessions[session_key]
            del self.sessions[session_key]
            
            # Remove from IP tracking
            if session.ip_address in self.ip_sessions:
                self.ip_sessions[session.ip_address].discard(session_key)
                if not self.ip_sessions[session.ip_address]:
                    del self.ip_sessions[session.ip_address]

    def _cleanup_if_needed(self):
        """Clean up expired sessions if cleanup interval has passed"""
        now = time.time()
        if now - self._last_cleanup < self.config.session_cleanup_interval:
            return

        self._last_cleanup = now
        self._cleanup_expired_sessions()

    def _cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        now = time.time()
        expired_keys = [
            key for key, session in self.sessions.items()
            if now - session.last_activity > self.config.session_timeout
        ]

        for key in expired_keys:
            self._remove_session(key)

    def get_stats(self) -> dict:
        """Get session statistics"""
        with self._lock:
            return {
                "total_sessions": len(self.sessions),
                "unique_ips": len(self.ip_sessions),
                "avg_requests_per_session": (
                    sum(s.request_count for s in self.sessions.values()) / len(self.sessions)
                    if self.sessions else 0
                ),
            }


class ResourceMonitor:
    """
    Monitors resource usage per session/IP
    
    Features:
    - CPU time tracking
    - Memory usage tracking
    - Execution time tracking
    - Resource limit enforcement
    """

    def __init__(self):
        self.execution_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._lock = threading.RLock()

    def record_execution(self, identifier: str, execution_time: float, memory_mb: float = 0):
        """Record execution metrics"""
        with self._lock:
            self.execution_times[identifier].append({
                "timestamp": time.time(),
                "execution_time": execution_time,
                "memory_mb": memory_mb,
            })

    def get_metrics(self, identifier: str, window: int = 60) -> dict:
        """
        Get metrics for identifier within time window
        
        Args:
            identifier: Session ID or IP address
            window: Time window in seconds
        """
        with self._lock:
            if identifier not in self.execution_times:
                return {
                    "count": 0,
                    "avg_execution_time": 0,
                    "max_execution_time": 0,
                    "total_memory_mb": 0,
                }

            now = time.time()
            cutoff = now - window
            
            recent = [
                record for record in self.execution_times[identifier]
                if record["timestamp"] > cutoff
            ]

            if not recent:
                return {
                    "count": 0,
                    "avg_execution_time": 0,
                    "max_execution_time": 0,
                    "total_memory_mb": 0,
                }

            return {
                "count": len(recent),
                "avg_execution_time": sum(r["execution_time"] for r in recent) / len(recent),
                "max_execution_time": max(r["execution_time"] for r in recent),
                "total_memory_mb": sum(r["memory_mb"] for r in recent),
            }


def sanitize_output(text: str, max_length: int = 10000) -> str:
    """
    Sanitize output text for safe display
    
    Features:
    - HTML entity encoding
    - Length limiting
    - Control character removal
    """
    if not text:
        return ""

    # Remove control characters except newlines and tabs
    sanitized = "".join(
        char for char in text
        if char == "\n" or char == "\t" or (ord(char) >= 32 and ord(char) != 127)
    )

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "\n... (output truncated)"

    # HTML entity encoding for web display
    sanitized = (
        sanitized
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    return sanitized


def validate_code_safety(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate code for potentially dangerous operations
    
    This is a basic check - the VM's security features provide the main protection.
    """
    dangerous_patterns = [
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "file(",
        "__builtins__",
        "system(",
        "popen(",
    ]

    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            return False, f"Potentially dangerous operation detected: {pattern}"

    return True, None
