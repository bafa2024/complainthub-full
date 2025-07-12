# backend/app/schemas.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import (
    RoleEnum,
    TicketStatusEnum,
    TicketCategoryEnum,
    TicketUrgencyEnum,
)

# Add these two new schemas for handling JWT tokens
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None


# -- User Schemas --
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: RoleEnum = RoleEnum.user


class UserCreate(UserBase):
    password: str
    brand_name: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    brand_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    tts_voice_id: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class NotificationPreferences(BaseModel):
    email_response: bool = True
    email_status: bool = True
    email_weekly: bool = False
    email_news: bool = False
    sms_urgent: bool = True
    sms_all: bool = False
    whatsapp_enable: bool = True
    push_notifications: bool = True
    marketing_emails: bool = False

class PrivacySettings(BaseModel):
    profile_visibility: str = "anonymous"  # anonymous, firstname, fullname
    share_analytics: bool = False
    share_location: bool = False
    allow_contact: bool = True
    data_retention: str = "1year"  # 6months, 1year, 2years, indefinite

class TicketTimelineEvent(BaseModel):
    id: int
    event_type: str
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[int] = None
    brand_id: Optional[int] = None

class TicketWithTimeline(BaseModel):
    timeline: List[TicketTimelineEvent] = []

class PublicComplaint(BaseModel):
    id: int
    title: str
    description: str
    brand_name: str
    category: str
    status: str
    urgency: str
    days_open: int
    created_at: datetime
    upvotes: int = 0
    comments_count: int = 0
    is_anonymous: bool = True
    user_alias: Optional[str] = None
    has_voice_recording: bool = False
    severity: str = "medium"

class ComplaintFilter(BaseModel):
    brand: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    date_range: Optional[str] = None
    search_query: Optional[str] = None
    days_open: Optional[int] = None
    urgency: Optional[str] = None
    severity: Optional[str] = None

class ComplaintStats(BaseModel):
    total_complaints: int
    unresolved_count: int
    resolved_count: int
    avg_resolution_time: Optional[float] = None
    resolution_rate: float
    top_brands: List[dict]
    category_distribution: List[dict]
    daily_trends: List[dict]


# -- Brand Schemas --
class BrandBase(BaseModel):
    name: str
    support_email: str
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    contact_info: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandCreateAdmin(BaseModel):
    name: str
    support_email: str
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    # Note: contact_info is excluded since the column doesn't exist in the database


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    support_email: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    contact_info: Optional[str] = None


class Brand(BrandBase):
    id: int
    credit_balance: float
    created_at: datetime

    class Config:
        orm_mode = True


# -- Team Invitation Schemas --
class TeamInvitationCreate(BaseModel):
    email: str
    role: RoleEnum = RoleEnum.brand_user


class TeamInvitationResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum
    brand_id: int
    invited_by: int
    is_accepted: bool
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TeamInvitationAccept(BaseModel):
    full_name: str
    password: str
    phone_number: Optional[str] = None


# -- Ticket Schemas --
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    channel: str


class TicketCreate(TicketBase):
    brand_id: int
    category: Optional[TicketCategoryEnum] = TicketCategoryEnum.complaint
    urgency: Optional[TicketUrgencyEnum] = TicketUrgencyEnum.medium


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatusEnum] = None
    category: Optional[TicketCategoryEnum] = None
    urgency: Optional[TicketUrgencyEnum] = None
    severity_level: Optional[int] = None  # 0-5 severity scale
    abuse_level_flag: Optional[bool] = None
    assignee_id: Optional[int] = None
    is_public: Optional[bool] = None


class Ticket(TicketBase):
    id: int
    owner_id: int
    brand_id: int
    assignee_id: Optional[int] = None
    status: TicketStatusEnum
    category: TicketCategoryEnum
    urgency: TicketUrgencyEnum
    severity_level: int  # 0-5 severity scale
    abuse_level_flag: bool
    satisfaction_rating: Optional[int] = None
    voice_recording_url: Optional[str] = None
    transcript: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    owner: User
    brand: Brand
    assignee: Optional[User] = None

    class Config:
        orm_mode = True

# Phone Number Schemas
class PhoneNumberBase(BaseModel):
    brand_id: int
    phone_number: str
    provider: str
    provider_id: Optional[str] = None
    country_code: str = "IN"
    area_code: Optional[str] = None
    number_type: str = "toll-free"
    capabilities: Optional[Dict[str, Any]] = None
    status: str = "active"
    monthly_cost: float = 0.0
    setup_cost: float = 0.0
    webhook_url: Optional[str] = None

class PhoneNumberCreate(PhoneNumberBase):
    pass

class PhoneNumberUpdate(BaseModel):
    status: Optional[str] = None
    webhook_url: Optional[str] = None
    monthly_cost: Optional[float] = None
    setup_cost: Optional[float] = None

class PhoneNumber(PhoneNumberBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TelephonyProviderBase(BaseModel):
    name: str
    display_name: str
    api_credentials: Optional[Dict[str, Any]] = None
    supported_countries: Optional[List[str]] = None
    supported_capabilities: Optional[List[str]] = None
    pricing: Optional[Dict[str, Any]] = None
    status: str = "active"

class TelephonyProviderCreate(TelephonyProviderBase):
    pass

class TelephonyProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    api_credentials: Optional[Dict[str, Any]] = None
    supported_countries: Optional[List[str]] = None
    supported_capabilities: Optional[List[str]] = None
    pricing: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TelephonyProvider(TelephonyProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PhoneNumberRequestBase(BaseModel):
    brand_id: int
    user_id: int
    country_code: str = "IN"
    area_code: Optional[str] = None
    number_type: str = "toll-free"
    capabilities: Optional[List[str]] = None
    provider_preference: Optional[str] = None

class PhoneNumberRequestCreate(PhoneNumberRequestBase):
    pass

class PhoneNumberRequestUpdate(BaseModel):
    status: Optional[str] = None
    assigned_number: Optional[str] = None
    provider_used: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

class PhoneNumberRequest(PhoneNumberRequestBase):
    id: int
    status: str
    assigned_number: Optional[str] = None
    provider_used: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AvailableNumber(BaseModel):
    phone_number: str
    provider: str
    country_code: str
    area_code: Optional[str] = None
    number_type: str
    capabilities: List[str]
    monthly_cost: float
    setup_cost: float
    features: List[str]

class NumberGenerationRequest(BaseModel):
    country_code: str = "IN"
    area_code: Optional[str] = None
    number_type: str = "toll-free"
    capabilities: List[str] = ["voice", "sms"]
    provider_preference: Optional[str] = None
    auto_approve: bool = False

class NumberGenerationResponse(BaseModel):
    success: bool
    phone_number: Optional[str] = None
    provider: Optional[str] = None
    cost: Optional[float] = None
    request_id: Optional[int] = None
    message: str

class FollowUpLogBase(BaseModel):
    ticket_id: int
    scheduled_time: datetime
    follow_up_type: str
    channel: str
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    user_telegram_id: Optional[str] = None
    brand_id: int
    parent_follow_up_id: Optional[int] = None

class FollowUpLogCreate(FollowUpLogBase):
    pass

class FollowUpLogUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_response: Optional[str] = None
    rating: Optional[int] = None
    responded_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    last_retry_at: Optional[datetime] = None

class FollowUpLog(FollowUpLogBase):
    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    last_retry_at: Optional[datetime] = None
    user_response: Optional[str] = None
    rating: Optional[int] = None
    responded_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FollowUpResponse(BaseModel):
    follow_up_id: int
    response: str
    rating: Optional[int] = None

class FollowUpStats(BaseModel):
    total_follow_ups: int
    successful: int
    failed: int
    pending: int
    success_rate: float
    channels: Dict[str, Dict[str, int]]
    period_days: int

class CRMIntegrationCreate(BaseModel):
    crm_type: str
    api_key: str
    base_url: str
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    brand_id: int
    is_active: bool = True
    sync_direction: str = "bidirectional"  # outbound, inbound, bidirectional
    auto_sync: bool = True

class CRMIntegrationUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_active: Optional[bool] = None
    sync_direction: Optional[str] = None
    auto_sync: Optional[bool] = None

class CRMIntegrationResponse(BaseModel):
    id: int
    crm_type: str
    brand_id: int
    is_active: bool
    sync_direction: str
    auto_sync: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CRMSyncRequest(BaseModel):
    crm_integration_id: int
    sync_direction: str = "bidirectional"  # outbound, inbound, bidirectional
    force_sync: bool = False

class CRMSyncResponse(BaseModel):
    success: bool
    message: str
    synced_tickets: int = 0
    errors: List[str] = []

class SecurityEvent(BaseModel):
    timestamp: str
    event_type: str
    details: Dict[str, Any]
    severity: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class SecurityReport(BaseModel):
    total_events: int
    threats_detected: int
    blocked_ips: int
    rate_limited_requests: int
    ddos_attacks: int
    recent_events: List[SecurityEvent]
    compliance_status: Dict[str, Any]

class ComplianceStatus(BaseModel):
    gdpr_compliant: bool
    data_retention_compliant: bool
    audit_trail_maintained: bool
    last_audit: str

class WAFRule(BaseModel):
    pattern: str
    description: str
    enabled: bool = True

class DDoSStatus(BaseModel):
    blocked_ips: int
    active_protection: bool
    threshold: int
    window: int

class SSLCertificate(BaseModel):
    valid: bool
    days_remaining: Optional[int] = None
    issuer: Optional[Dict[str, str]] = None
    subject: Optional[Dict[str, str]] = None
    error: Optional[str] = None

class GDPRConsent(BaseModel):
    consent_type: str
    granted: bool
    timestamp: str
    recorded_by: str

class DataAccessLog(BaseModel):
    timestamp: str
    user_id: str
    data_type: str
    action: str

class WebhookRequest(BaseModel):
    user_id: str
    phone_number: Optional[str] = None
    session_id: Optional[str] = None
    message: Optional[str] = None
    message_id: Optional[str] = None
    user_name: Optional[str] = None
    media_url: Optional[str] = None
    recording_url: Optional[str] = None
    channel: Optional[str] = None
    brand_id: Optional[int] = None