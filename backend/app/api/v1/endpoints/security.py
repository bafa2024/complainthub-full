# backend/app/api/v1/endpoints/security.py

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.core.security import security_manager, SECURITY_EVENTS, IP_BLACKLIST
from app.models import User, Brand
from app.schemas import SecurityEvent, SecurityReport, ComplianceStatus
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/events", response_model=List[SecurityEvent])
async def get_security_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get security events (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        events = security_manager.audit_log
        
        # Filter by date range
        if start_date:
            events = [e for e in events if datetime.fromisoformat(e["timestamp"]) >= start_date]
        if end_date:
            events = [e for e in events if datetime.fromisoformat(e["timestamp"]) <= end_date]
        
        # Filter by event type
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        # Filter by severity
        if severity:
            events = [e for e in events if e["severity"] == severity]
        
        # Limit results
        events = events[-limit:]
        
        return events
        
    except Exception as e:
        logger.error(f"Error getting security events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report", response_model=SecurityReport)
async def get_security_report(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get comprehensive security report (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return security_manager.get_security_report()
        
    except Exception as e:
        logger.error(f"Error getting security report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance", response_model=ComplianceStatus)
async def get_compliance_status(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get compliance status (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return security_manager.compliance.get_status()
        
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blacklist/ip")
async def add_ip_to_blacklist(
    ip_address: str,
    reason: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Add IP to blacklist (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate IP address
        import ipaddress
        ipaddress.ip_address(ip_address)
        
        IP_BLACKLIST.add(ip_address)
        
        # Log the action
        security_manager.log_security_event("MANUAL_BLACKLIST", {
            "ip_address": ip_address,
            "reason": reason,
            "admin_user": current_user.get("id")
        }, "INFO")
        
        return {"message": f"IP {ip_address} added to blacklist"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")
    except Exception as e:
        logger.error(f"Error adding IP to blacklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/blacklist/ip/{ip_address}")
async def remove_ip_from_blacklist(
    ip_address: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Remove IP from blacklist (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if ip_address in IP_BLACKLIST:
            IP_BLACKLIST.remove(ip_address)
            
            # Log the action
            security_manager.log_security_event("REMOVE_BLACKLIST", {
                "ip_address": ip_address,
                "admin_user": current_user.get("id")
            }, "INFO")
            
            return {"message": f"IP {ip_address} removed from blacklist"}
        else:
            raise HTTPException(status_code=404, detail="IP not found in blacklist")
        
    except Exception as e:
        logger.error(f"Error removing IP from blacklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blacklist")
async def get_blacklisted_ips(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get list of blacklisted IPs (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return {"blacklisted_ips": list(IP_BLACKLIST)}
        
    except Exception as e:
        logger.error(f"Error getting blacklisted IPs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rate-limit/reset")
async def reset_rate_limit(
    identifier: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Reset rate limit for an identifier (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if identifier in security_manager.rate_limit_store:
            del security_manager.rate_limit_store[identifier]
            
            # Log the action
            security_manager.log_security_event("RATE_LIMIT_RESET", {
                "identifier": identifier,
                "admin_user": current_user.get("id")
            }, "INFO")
            
            return {"message": f"Rate limit reset for {identifier}"}
        else:
            raise HTTPException(status_code=404, detail="Identifier not found")
        
    except Exception as e:
        logger.error(f"Error resetting rate limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ssl/check")
async def check_ssl_certificate(
    hostname: str,
    port: int = 443,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Check SSL certificate validity (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = security_manager.ssl_monitor.check_certificate(hostname, port)
        return result
        
    except Exception as e:
        logger.error(f"Error checking SSL certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/threat-intelligence/update")
async def update_threat_intelligence(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Update threat intelligence feeds (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        background_tasks.add_task(security_manager.threat_intelligence.update_feeds)
        return {"message": "Threat intelligence update started"}
        
    except Exception as e:
        logger.error(f"Error updating threat intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ddos/status")
async def get_ddos_status(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get DDoS protection status (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return {
            "blocked_ips": len(security_manager.ddos_protection.blocked_ips),
            "active_protection": True,
            "threshold": security_manager.ddos_protection.threshold,
            "window": security_manager.ddos_protection.window
        }
        
    except Exception as e:
        logger.error(f"Error getting DDoS status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waf/rules")
async def update_waf_rules(
    rules: List[str],
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Update WAF rules (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        security_manager.waf.blocked_patterns = rules
        
        # Log the action
        security_manager.log_security_event("WAF_RULES_UPDATE", {
            "rules_count": len(rules),
            "admin_user": current_user.get("id")
        }, "INFO")
        
        return {"message": f"WAF rules updated with {len(rules)} rules"}
        
    except Exception as e:
        logger.error(f"Error updating WAF rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/waf/rules")
async def get_waf_rules(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get current WAF rules (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return {"rules": security_manager.waf.blocked_patterns}
        
    except Exception as e:
        logger.error(f"Error getting WAF rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/gdpr-consent")
async def record_gdpr_consent(
    user_id: int,
    consent_type: str,
    granted: bool,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Record GDPR consent (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        security_manager.compliance.gdpr_consent[user_id] = {
            "consent_type": consent_type,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
            "recorded_by": current_user.get("id")
        }
        
        return {"message": "GDPR consent recorded"}
        
    except Exception as e:
        logger.error(f"Error recording GDPR consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/gdpr-consent/{user_id}")
async def get_gdpr_consent(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get GDPR consent for user (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return security_manager.compliance.gdpr_consent.get(user_id, {})
        
    except Exception as e:
        logger.error(f"Error getting GDPR consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit/data-access")
async def log_data_access(
    user_id: str,
    data_type: str,
    action: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Log data access for compliance (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        security_manager.compliance.log_data_access(user_id, data_type, action)
        return {"message": "Data access logged"}
        
    except Exception as e:
        logger.error(f"Error logging data access: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/trail")
async def get_audit_trail(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get compliance audit trail (admin only)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        trail = security_manager.compliance.audit_trail
        
        # Filter by date range
        if start_date:
            trail = [e for e in trail if datetime.fromisoformat(e["timestamp"]) >= start_date]
        if end_date:
            trail = [e for e in trail if datetime.fromisoformat(e["timestamp"]) <= end_date]
        
        # Limit results
        trail = trail[-limit:]
        
        return {"audit_trail": trail}
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 