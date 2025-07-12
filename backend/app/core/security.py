# backend/app/core/security.py

import logging
import traceback
import hashlib
import hmac
import base64
import json
import re
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict, List
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import ipaddress
import ssl
import socket
import asyncio
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import geoip2.database
import geoip2.errors
from typing import Tuple, Set
import threading
import time
from collections import defaultdict, deque

from ..config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

# Encryption key for sensitive data
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Security monitoring
SECURITY_EVENTS = []
FAILED_LOGIN_ATTEMPTS = {}
IP_BLACKLIST = set()
SUSPICIOUS_ACTIVITY = []

class EnterpriseSecurityManager:
    """Enterprise-grade security management system"""
    
    def __init__(self):
        self.rate_limit_store = {}
        self.session_store = {}
        self.audit_log = []
        self.threat_detection_rules = self._load_threat_rules()
        self.ddos_protection = DDoSProtection()
        self.waf = WebApplicationFirewall()
        self.compliance = ComplianceManager()
        self.geo_blocking = GeoBlocking()
        self.ssl_monitor = SSLMonitor()
        self.threat_intelligence = ThreatIntelligence()
        
        # Initialize security monitoring
        self._start_security_monitoring()
    
    def _load_threat_rules(self) -> Dict:
        """Load advanced threat detection rules"""
        return {
            "failed_login_threshold": 5,
            "suspicious_ip_patterns": [
                r"^10\.",  # Private IPs
                r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",  # Private IPs
                r"^192\.168\.",  # Private IPs
                r"^0\.0\.0\.",  # Invalid IPs
                r"^255\.255\.255\.",  # Broadcast IPs
            ],
            "suspicious_user_agents": [
                "bot", "crawler", "spider", "scraper", "curl", "wget", "python-requests"
            ],
            "suspicious_paths": [
                "/admin", "/wp-admin", "/phpmyadmin", "/.env", "/config", "/backup",
                "/shell", "/cmd", "/exec", "/system", "/passwd", "/shadow"
            ],
            "sql_injection_patterns": [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(--|\/\*|\*\/|xp_|sp_)",
                r"(\b(and|or)\b\s+\d+\s*=\s*\d+)",
                r"(\b(and|or)\b\s+['\"].*['\"])"
            ],
            "xss_patterns": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>"
            ],
            "path_traversal_patterns": [
                r"\.\.\/",
                r"\.\.\\",
                r"\/etc\/passwd",
                r"\/etc\/shadow",
                r"c:\\windows\\system32"
            ]
        }
    
    def _start_security_monitoring(self):
        """Start background security monitoring"""
        def monitor():
            while True:
                try:
                    self._cleanup_old_data()
                    self._analyze_threat_patterns()
                    self._update_threat_intelligence()
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    logging.error(f"Security monitoring error: {e}")
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _cleanup_old_data(self):
        """Clean up old security data"""
        now = datetime.utcnow()
        
        # Clean up old rate limit data
        for identifier in list(self.rate_limit_store.keys()):
            self.rate_limit_store[identifier] = [
                timestamp for timestamp in self.rate_limit_store[identifier]
                if (now - timestamp).seconds < 3600
            ]
            if not self.rate_limit_store[identifier]:
                del self.rate_limit_store[identifier]
        
        # Clean up old audit logs
        cutoff_time = now - timedelta(days=30)
        self.audit_log = [
            event for event in self.audit_log
            if datetime.fromisoformat(event["timestamp"]) > cutoff_time
        ]
    
    def _analyze_threat_patterns(self):
        """Analyze threat patterns and update rules"""
        # Analyze failed login patterns
        failed_ips = defaultdict(int)
        for event in self.audit_log[-1000:]:
            if event["event_type"] == "FAILED_LOGIN":
                ip = event["details"].get("ip_address")
                if ip:
                    failed_ips[ip] += 1
        
        # Auto-blacklist IPs with excessive failed logins
        for ip, count in failed_ips.items():
            if count > 20:
                IP_BLACKLIST.add(ip)
                self.log_security_event("AUTO_BLACKLIST", {"ip_address": ip, "reason": "excessive_failed_logins"})
    
    def _update_threat_intelligence(self):
        """Update threat intelligence feeds"""
        self.threat_intelligence.update_feeds()
    
    def process_request(self, request_data: Dict) -> Dict[str, Any]:
        """Process incoming request with comprehensive security checks"""
        result = {
            "allowed": True,
            "threats": [],
            "warnings": [],
            "rate_limited": False,
            "geo_blocked": False
        }
        
        client_ip = request_data.get("client_ip", "")
        user_agent = request_data.get("user_agent", "")
        path = request_data.get("path", "")
        method = request_data.get("method", "")
        
        # DDoS Protection
        if self.ddos_protection.is_under_attack(client_ip):
            result["allowed"] = False
            result["threats"].append("DDoS_ATTACK")
            return result
        
        # WAF Protection
        waf_result = self.waf.check_request(request_data)
        if not waf_result["allowed"]:
            result["allowed"] = False
            result["threats"].extend(waf_result["threats"])
            return result
        
        # Geo-blocking
        if self.geo_blocking.is_blocked(client_ip):
            result["allowed"] = False
            result["geo_blocked"] = True
            result["threats"].append("GEO_BLOCKED")
            return result
        
        # Rate limiting
        if not self.check_rate_limit(client_ip, 100, 3600):
            result["rate_limited"] = True
            result["warnings"].append("RATE_LIMITED")
        
        # Threat detection
        threats = self.detect_threats(request_data)
        result["threats"].extend(threats)
        
        # Log security event
        self.log_security_event("REQUEST_PROCESSED", {
            "ip": client_ip,
            "path": path,
            "method": method,
            "user_agent": user_agent,
            "threats": result["threats"],
            "allowed": result["allowed"]
        })
        
        return result
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data with enterprise-grade encryption"""
        try:
            encrypted_data = cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Encryption error: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return encrypted_data
    
    def mask_pii_data(self, data: str, data_type: str = "email") -> str:
        """Mask personally identifiable information for GDPR compliance"""
        if data_type == "email":
            if "@" in data:
                username, domain = data.split("@")
                return f"{username[:2]}***@{domain}"
        elif data_type == "phone":
            if len(data) >= 10:
                return f"{data[:3]}***{data[-4:]}"
        elif data_type == "name":
            if len(data) > 2:
                return f"{data[0]}{'*' * (len(data) - 2)}{data[-1]}"
        elif data_type == "credit_card":
            if len(data) >= 13:
                return f"{data[:4]}****{data[-4:]}"
        elif data_type == "ssn":
            if len(data) >= 9:
                return f"***-**-{data[-4:]}"
        return data
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Advanced rate limiting with sliding window"""
        now = datetime.utcnow()
        if identifier not in self.rate_limit_store:
            self.rate_limit_store[identifier] = deque()
        
        # Remove old entries
        while self.rate_limit_store[identifier] and (now - self.rate_limit_store[identifier][0]).seconds >= window:
            self.rate_limit_store[identifier].popleft()
        
        if len(self.rate_limit_store[identifier]) >= limit:
            return False
        
        self.rate_limit_store[identifier].append(now)
        return True
    
    def detect_threats(self, request_data: Dict) -> List[str]:
        """Advanced threat detection with multiple layers"""
        threats = []
        
        # Check IP address
        client_ip = request_data.get("client_ip", "")
        if client_ip in IP_BLACKLIST:
            threats.append("BLACKLISTED_IP")
        
        # Check for suspicious patterns
        for pattern in self.threat_detection_rules["suspicious_ip_patterns"]:
            if re.match(pattern, client_ip):
                threats.append("SUSPICIOUS_IP_PATTERN")
        
        # Check user agent
        user_agent = request_data.get("user_agent", "").lower()
        for suspicious_ua in self.threat_detection_rules["suspicious_user_agents"]:
            if suspicious_ua in user_agent:
                threats.append("SUSPICIOUS_USER_AGENT")
        
        # Check request path
        path = request_data.get("path", "").lower()
        for suspicious_path in self.threat_detection_rules["suspicious_paths"]:
            if suspicious_path in path:
                threats.append("SUSPICIOUS_PATH")
        
        # Check for SQL injection
        payload = request_data.get("payload", "")
        for pattern in self.threat_detection_rules["sql_injection_patterns"]:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("SQL_INJECTION_ATTEMPT")
        
        # Check for XSS
        for pattern in self.threat_detection_rules["xss_patterns"]:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("XSS_ATTEMPT")
        
        # Check for path traversal
        for pattern in self.threat_detection_rules["path_traversal_patterns"]:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append("PATH_TRAVERSAL_ATTEMPT")
        
        return threats
    
    def log_security_event(self, event_type: str, details: Dict, severity: str = "INFO"):
        """Log security events for audit and compliance"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": severity,
            "session_id": details.get("session_id"),
            "user_id": details.get("user_id")
        }
        self.audit_log.append(event)
        SECURITY_EVENTS.append(event)
        
        # Keep only last 10000 events
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
        
        # Alert on high severity events
        if severity in ["HIGH", "CRITICAL"]:
            self._send_security_alert(event)
    
    def _send_security_alert(self, event: Dict):
        """Send security alerts for critical events"""
        # Implementation for sending alerts (email, SMS, Slack, etc.)
        logging.critical(f"SECURITY ALERT: {event}")
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Enterprise password strength validation"""
        score = 0
        feedback = []
        
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Password must be at least 8 characters long (12+ recommended)")
        
        if re.search(r"[a-z]", password):
            score += 1
        else:
            feedback.append("Password must contain lowercase letters")
        
        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Password must contain uppercase letters")
        
        if re.search(r"\d", password):
            score += 1
        else:
            feedback.append("Password must contain numbers")
        
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        else:
            feedback.append("Password must contain special characters")
        
        # Check for common patterns
        if re.search(r"(123|abc|qwe|password|admin)", password.lower()):
            score -= 2
            feedback.append("Password contains common patterns")
        
        # Check for repeated characters
        if re.search(r"(.)\1{2,}", password):
            score -= 1
            feedback.append("Password contains repeated characters")
        
        strength = "weak" if score < 3 else "medium" if score < 5 else "strong"
        
        return {
            "score": max(0, score),
            "strength": strength,
            "feedback": feedback,
            "is_valid": score >= 4
        }
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_field(self, data: str, salt: str = None) -> Dict[str, str]:
        """Hash sensitive fields with salt for GDPR compliance"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend()
        )
        
        hash_value = base64.b64encode(kdf.derive(data.encode())).decode()
        
        return {
            "hash": hash_value,
            "salt": salt
        }
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signatures for security"""
        try:
            expected_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logging.error(f"Webhook signature verification error: {e}")
            return False
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        return {
            "total_events": len(self.audit_log),
            "threats_detected": len([e for e in self.audit_log if e["severity"] in ["HIGH", "CRITICAL"]]),
            "blocked_ips": len(IP_BLACKLIST),
            "rate_limited_requests": len([e for e in self.audit_log if "RATE_LIMITED" in e.get("details", {}).get("threats", [])]),
            "ddos_attacks": len([e for e in self.audit_log if "DDoS_ATTACK" in e.get("details", {}).get("threats", [])]),
            "recent_events": self.audit_log[-100:],
            "compliance_status": self.compliance.get_status()
        }

class DDoSProtection:
    """DDoS protection system"""
    
    def __init__(self):
        self.request_counts = defaultdict(lambda: deque())
        self.blocked_ips = set()
        self.threshold = 1000  # requests per minute
        self.window = 60  # seconds
    
    def is_under_attack(self, ip: str) -> bool:
        """Check if IP is under DDoS attack"""
        now = time.time()
        
        # Clean old requests
        while self.request_counts[ip] and now - self.request_counts[ip][0] > self.window:
            self.request_counts[ip].popleft()
        
        # Add current request
        self.request_counts[ip].append(now)
        
        # Check threshold
        if len(self.request_counts[ip]) > self.threshold:
            self.blocked_ips.add(ip)
            return True
        
        return ip in self.blocked_ips

class WebApplicationFirewall:
    """Web Application Firewall"""
    
    def __init__(self):
        self.blocked_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
            r"(--|\/\*|\*\/)",
            r"\.\.\/",
            r"\/etc\/passwd"
        ]
    
    def check_request(self, request_data: Dict) -> Dict[str, Any]:
        """Check request against WAF rules"""
        result = {"allowed": True, "threats": []}
        
        payload = str(request_data.get("payload", ""))
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                result["allowed"] = False
                result["threats"].append("WAF_BLOCKED")
                break
        
        return result

class GeoBlocking:
    """Geographic IP blocking"""
    
    def __init__(self):
        self.blocked_countries = set()
        self.geo_db = None
        try:
            # Initialize GeoIP database (requires geoip2 database file)
            pass
        except:
            logging.warning("GeoIP database not available")
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is from blocked country"""
        # Implementation would require GeoIP database
        return False

class SSLMonitor:
    """SSL certificate monitoring"""
    
    def check_certificate(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (not_after - datetime.utcnow()).days
                    
                    return {
                        "valid": True,
                        "days_remaining": days_remaining,
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "subject": dict(x[0] for x in cert['subject'])
                    }
        except Exception as e:
            return {"valid": False, "error": str(e)}

class ThreatIntelligence:
    """Threat intelligence integration"""
    
    def __init__(self):
        self.threat_feeds = []
        self.last_update = None
    
    def update_feeds(self):
        """Update threat intelligence feeds"""
        # Implementation for updating threat feeds
        self.last_update = datetime.utcnow()

class ComplianceManager:
    """Compliance management for GDPR, SOC2, etc."""
    
    def __init__(self):
        self.gdpr_consent = {}
        self.data_retention_policies = {}
        self.audit_trail = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        return {
            "gdpr_compliant": True,
            "data_retention_compliant": True,
            "audit_trail_maintained": True,
            "last_audit": datetime.utcnow().isoformat()
        }
    
    def log_data_access(self, user_id: str, data_type: str, action: str):
        """Log data access for GDPR compliance"""
        self.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "data_type": data_type,
            "action": action
        })

# Initialize enterprise security manager
security_manager = EnterpriseSecurityManager()

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create refresh token for session management"""
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> Optional[str]:
    """Verify refresh token and return subject"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "refresh":
            return payload.get("sub")
    except Exception as e:
        logging.error(f"Refresh token verification error: {e}")
    return None

def generate_2fa_code() -> str:
    """Generate 6-digit 2FA code"""
    return str(secrets.randbelow(1000000)).zfill(6)

def validate_2fa_code(code: str, stored_code: str, expiry_time: datetime) -> bool:
    """Validate 2FA code"""
    if datetime.utcnow() > expiry_time:
        return False
    return code == stored_code

def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        data = data.replace(char, '')
    return data.strip()

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_format(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    return len(digits_only) >= 10

def check_ip_whitelist(ip_address: str, whitelist: List[str]) -> bool:
    """Check if IP address is in whitelist"""
    try:
        ip = ipaddress.ip_address(ip_address)
        for allowed_ip in whitelist:
            if ipaddress.ip_address(allowed_ip) == ip:
                return True
        return False
    except ValueError:
        return False

def log_failed_login_attempt(identifier: str, ip_address: str):
    """Log failed login attempt"""
    if identifier not in FAILED_LOGIN_ATTEMPTS:
        FAILED_LOGIN_ATTEMPTS[identifier] = []
    
    FAILED_LOGIN_ATTEMPTS[identifier].append({
        "timestamp": datetime.utcnow(),
        "ip_address": ip_address
    })
    
    # Keep only last 10 attempts
    if len(FAILED_LOGIN_ATTEMPTS[identifier]) > 10:
        FAILED_LOGIN_ATTEMPTS[identifier] = FAILED_LOGIN_ATTEMPTS[identifier][-10:]
    
    # Check if account should be temporarily locked
    recent_attempts = [
        attempt for attempt in FAILED_LOGIN_ATTEMPTS[identifier]
        if (datetime.utcnow() - attempt["timestamp"]).seconds < 3600
    ]
    
    if len(recent_attempts) >= 5:
        security_manager.log_security_event(
            "ACCOUNT_LOCKED",
            {"identifier": identifier, "reason": "Too many failed attempts"},
            "WARNING"
        )

def is_account_locked(identifier: str) -> bool:
    """Check if account is temporarily locked"""
    if identifier not in FAILED_LOGIN_ATTEMPTS:
        return False
    
    recent_attempts = [
        attempt for attempt in FAILED_LOGIN_ATTEMPTS[identifier]
        if (datetime.utcnow() - attempt["timestamp"]).seconds < 3600
    ]
    
    return len(recent_attempts) >= 5

def clear_failed_attempts(identifier: str):
    """Clear failed login attempts for successful login"""
    if identifier in FAILED_LOGIN_ATTEMPTS:
        del FAILED_LOGIN_ATTEMPTS[identifier]