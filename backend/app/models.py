import enum
import json
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db.base_class import Base
from datetime import datetime

class RoleEnum(enum.Enum):
    user = "user"
    brand_user = "brand_user"
    admin = "admin"

class TicketStatusEnum(enum.Enum):
    new = "new"
    open = "open"
    in_progress = "in-progress"
    resolved = "resolved"
    closed = "closed"

class TicketCategoryEnum(enum.Enum):
    complaint = "Complaint"
    feedback = "Feedback"
    suggestion = "Suggestion"
    support = "Support"

class TicketUrgencyEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    support_email = Column(String, unique=True, index=True, nullable=False)
    credit_balance = Column(Float, nullable=False, default=0.0)
    industry = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    billing_address = Column(JSON, nullable=True)
    tax_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tickets = relationship("Ticket", back_populates="brand")
    brand_users = relationship("User", back_populates="brand")
    team_invitations = relationship("TeamInvitation", back_populates="brand")
    transactions = relationship("Transaction", back_populates="brand")
    subscriptions = relationship("Subscription", back_populates="brand")
    payment_methods = relationship("PaymentMethod", back_populates="brand")
    phone_numbers = relationship("PhoneNumber", back_populates="brand")
    phone_number_requests = relationship("PhoneNumberRequest", back_populates="brand")
    follow_ups = relationship("FollowUpLog", back_populates="brand")
    ai_learning_data = relationship("AILearningData", back_populates="brand")
    conversation_patterns = relationship("ConversationPattern", back_populates="brand")
    brand_knowledge = relationship("BrandKnowledge", back_populates="brand")
    ai_response_templates = relationship("AIResponseTemplate", back_populates="brand")
    user_interactions = relationship("UserInteraction", back_populates="brand")
    conversation_sessions = relationship("ConversationSession", back_populates="brand")
    follow_up_templates = relationship("FollowUpTemplate", back_populates="brand")
    email_outreach_logs = relationship("EmailOutreachLog", back_populates="brand")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    tts_voice_id = Column(String, nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    two_factor_enabled_at = Column(DateTime(timezone=True), nullable=True)
    two_factor_disabled_at = Column(DateTime(timezone=True), nullable=True)
    
    # GDPR consent fields
    marketing_consent = Column(Boolean, default=False)
    data_processing_consent = Column(Boolean, default=True)
    third_party_consent = Column(Boolean, default=False)
    consent_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="brand_users")
    tickets = relationship("Ticket", foreign_keys="[Ticket.owner_id]", back_populates="owner")
    assigned_tickets = relationship("Ticket", foreign_keys="[Ticket.assignee_id]", back_populates="assignee")
    security_events = relationship("SecurityEvent", back_populates="user")
    consents = relationship("UserConsent", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")
    phone_number_requests = relationship("PhoneNumberRequest", back_populates="user")
    conversation_sessions = relationship("ConversationSession", back_populates="user")

class TeamInvitation(Base):
    __tablename__ = "team_invitations"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.brand_user)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitation_token = Column(String, unique=True, index=True, nullable=False)
    is_accepted = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    brand = relationship("Brand", back_populates="team_invitations")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(Enum(TicketStatusEnum), default=TicketStatusEnum.new)
    category = Column(Enum(TicketCategoryEnum), default=TicketCategoryEnum.complaint)
    urgency = Column(Enum(TicketUrgencyEnum), default=TicketUrgencyEnum.medium)
    severity_level = Column(Integer, default=1)  # 0-5 severity scale
    abuse_level_flag = Column(Boolean, default=False)
    channel = Column(String, nullable=False)
    satisfaction_rating = Column(Integer, nullable=True)
    voice_recording_url = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # GDPR compliance
    owner = relationship("User", foreign_keys=[owner_id], back_populates="tickets")
    brand = relationship("Brand", back_populates="tickets")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tickets")
    transactions = relationship("Transaction", back_populates="ticket")
    follow_ups = relationship("FollowUpLog", back_populates="ticket")
    ai_learning_data = relationship("AILearningData", back_populates="ticket")
    crm_integrations = relationship("CRMIntegration", back_populates="ticket")
    conversation_sessions = relationship("ConversationSession", back_populates="ticket")

# Billing and Payment Models

class TransactionStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"

class TransactionTypeEnum(enum.Enum):
    credit_topup = "credit_topup"
    complaint_charge = "complaint_charge"
    subscription_payment = "subscription_payment"
    refund = "refund"
    adjustment = "adjustment"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    type = Column(Enum(TransactionTypeEnum), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatusEnum), default=TransactionStatusEnum.pending)
    description = Column(Text, nullable=True)
    payment_intent_id = Column(String, nullable=True)
    stripe_refund_id = Column(String, nullable=True)
    meta_info = Column('metadata', JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    brand = relationship("Brand", back_populates="transactions")
    ticket = relationship("Ticket", back_populates="transactions")

class SubscriptionStatusEnum(enum.Enum):
    active = "active"
    cancelled = "cancelled"
    past_due = "past_due"
    unpaid = "unpaid"
    trialing = "trialing"

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True, index=True, nullable=False)
    plan_type = Column(String, nullable=False)  # basic, professional, enterprise
    status = Column(Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.active)
    credits_per_month = Column(Integer, nullable=False)
    monthly_price = Column(Float, nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    meta_info = Column('metadata', JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    brand = relationship("Brand", back_populates="subscriptions")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    stripe_payment_method_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # card, bank_account, etc.
    last4 = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    is_default = Column(Boolean, default=False)
    meta_info = Column('metadata', JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    brand = relationship("Brand", back_populates="payment_methods")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="draft")  # draft, sent, paid, overdue, cancelled
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    items = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Self-Learning and AI Models

class AILearningData(Base):
    __tablename__ = "ai_learning_data"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    user_message = Column(Text, nullable=False)
    ai_prediction = Column(JSON, nullable=False)  # Store full AI analysis
    actual_outcome = Column(JSON, nullable=True)  # Store actual resolution
    confidence_score = Column(Float, nullable=True)
    language = Column(String, default="en")
    channel = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="ai_learning_data")
    ticket = relationship("Ticket", back_populates="ai_learning_data")

class ConversationPattern(Base):
    __tablename__ = "conversation_patterns"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    pattern_type = Column(String, nullable=False)  # question, response, resolution
    pattern_text = Column(Text, nullable=False)
    pattern_hash = Column(String, unique=True, index=True, nullable=False)
    frequency = Column(Integer, default=1)
    success_rate = Column(Float, default=0.0)
    avg_resolution_time = Column(Float, nullable=True)  # in hours
    category = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    language = Column(String, default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="conversation_patterns")

class ModelTrainingRecord(Base):
    __tablename__ = "model_training_records"
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, nullable=False)  # intent_classifier, urgency_classifier
    training_samples = Column(Integer, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_duration = Column(Float, nullable=True)  # in seconds
    model_version = Column(String, nullable=False)
    model_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Training parameters
    parameters = Column(JSON, nullable=True)

class BrandKnowledge(Base):
    __tablename__ = "brand_knowledge"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    knowledge_type = Column(String, nullable=False)  # faq, common_issues, product_info
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # Array of keywords
    confidence_score = Column(Float, default=1.0)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    language = Column(String, default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="brand_knowledge")

class AIResponseTemplate(Base):
    __tablename__ = "ai_response_templates"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    template_name = Column(String, nullable=False)
    template_text = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    language = Column(String, default="en")
    variables = Column(JSON, nullable=True)  # Template variables
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="ai_response_templates")

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    session_id = Column(String, nullable=False)
    interaction_type = Column(String, nullable=False)  # message, voice, satisfaction_rating
    content = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    satisfaction_score = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)  # in seconds
    channel = Column(String, nullable=False)
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    brand = relationship("Brand", back_populates="user_interactions")

# Security and Compliance Models

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    severity = Column(String, default="medium")  # low, medium, high, critical
    context = Column(JSON, nullable=True)  # Additional event data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="security_events")
    admin = relationship("Admin", back_populates="security_events")

class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String, nullable=False)  # user_data, ticket_data, message_data, etc.
    retention_period_days = Column(Integer, nullable=False)
    auto_deletion = Column(Boolean, default=True)
    deletion_trigger = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DataBreachReport(Base):
    __tablename__ = "data_breach_reports"
    id = Column(Integer, primary_key=True, index=True)
    breach_id = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    affected_users = Column(Integer, nullable=False)
    breach_date = Column(DateTime(timezone=True), nullable=False)
    discovery_date = Column(DateTime(timezone=True), nullable=False)
    notification_date = Column(DateTime(timezone=True), nullable=True)
    severity = Column(String, default="medium")  # low, medium, high, critical
    status = Column(String, default="reported")  # reported, investigating, contained, resolved
    containment_measures = Column(JSON, nullable=True)
    affected_data_types = Column(JSON, nullable=True)
    reported_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("Admin", back_populates="breach_reports")

class UserConsent(Base):
    __tablename__ = "user_consents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(String, nullable=False)  # marketing, data_processing, third_party
    granted = Column(Boolean, default=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="consents")

class IPWhitelist(Base):
    __tablename__ = "ip_whitelist"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    added_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="ip_whitelist_entries")

class IPBlacklist(Base):
    __tablename__ = "ip_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True, nullable=False)
    reason = Column(Text, nullable=True)
    threat_level = Column(String, default="medium")  # low, medium, high
    added_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="ip_blacklist_entries")

class FailedLoginAttempt(Base):
    __tablename__ = "failed_login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, nullable=False, index=True)  # email or IP
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    attempt_count = Column(Integer, default=1)
    first_attempt = Column(DateTime(timezone=True), server_default=func.now())
    last_attempt = Column(DateTime(timezone=True), server_default=func.now())
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")  # admin, super_admin
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Security fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    ip_whitelist_enabled = Column(Boolean, default=True)
    
    # Relationships
    security_events = relationship("SecurityEvent", back_populates="admin")
    breach_reports = relationship("DataBreachReport", back_populates="admin")
    ip_whitelist_entries = relationship("IPWhitelist", back_populates="admin")
    ip_blacklist_entries = relationship("IPBlacklist", back_populates="admin")

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)  # twilio, knowlarity, exotel, etc.
    provider_id = Column(String)  # Provider's internal ID for this number
    country_code = Column(String, default="IN")
    area_code = Column(String)
    number_type = Column(String, default="toll-free")  # toll-free, local, mobile
    capabilities = Column(JSON)  # voice, sms, whatsapp
    status = Column(String, default="active")  # active, inactive, pending
    monthly_cost = Column(Float, default=0.0)
    setup_cost = Column(Float, default=0.0)
    webhook_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="phone_numbers")

class TelephonyProvider(Base):
    __tablename__ = "telephony_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # twilio, knowlarity, exotel, etc.
    display_name = Column(String, nullable=False)
    api_credentials = Column(JSON)  # Encrypted API keys and tokens
    supported_countries = Column(JSON)  # List of supported country codes
    supported_capabilities = Column(JSON)  # voice, sms, whatsapp
    pricing = Column(JSON)  # Monthly and setup costs
    status = Column(String, default="active")  # active, inactive, maintenance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PhoneNumberRequest(Base):
    __tablename__ = "phone_number_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country_code = Column(String, default="IN")
    area_code = Column(String)
    number_type = Column(String, default="toll-free")
    capabilities = Column(JSON)  # voice, sms, whatsapp
    provider_preference = Column(String)  # Preferred provider
    status = Column(String, default="pending")  # pending, approved, rejected, completed
    assigned_number = Column(String)  # The actual phone number assigned
    provider_used = Column(String)
    cost = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="phone_number_requests")
    user = relationship("User", back_populates="phone_number_requests")

class FollowUpLog(Base):
    __tablename__ = "follow_up_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, failed
    follow_up_type = Column(String, nullable=False)  # resolution_confirmation, secondary_follow_up, rating_request
    channel = Column(String, nullable=False)  # voice, whatsapp, email, telegram, webchat
    user_phone = Column(String)
    user_email = Column(String)
    user_telegram_id = Column(String)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    parent_follow_up_id = Column(Integer, ForeignKey("follow_up_logs.id"))
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    user_response = Column(String)
    rating = Column(Integer)
    responded_at = Column(DateTime)
    result = Column(Text)  # JSON result of follow-up execution
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="follow_ups")
    brand = relationship("Brand", back_populates="follow_ups")
    parent_follow_up = relationship("FollowUpLog", remote_side=[id])
    child_follow_ups = relationship("FollowUpLog", back_populates="parent_follow_up")

class CRMIntegration(Base):
    __tablename__ = "crm_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    crm_type = Column(String, nullable=False)  # salesforce, zoho, freshworks, etc.
    crm_case_id = Column(String, nullable=False)
    meta_info = Column('metadata', Text)  # JSON string with additional CRM data
    sync_status = Column(String, default="synced")  # synced, pending, failed
    last_sync = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="crm_integrations")

# Contextual Follow-Ups and Session Continuity Models

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    channel = Column(String, nullable=False)  # web, telegram, whatsapp, etc.
    language = Column(String, default="en")
    status = Column(String, default="active")  # active, completed, abandoned
    context_summary = Column(Text, nullable=True)  # AI-generated summary of conversation
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="conversation_sessions")
    user = relationship("User", back_populates="conversation_sessions")
    ticket = relationship("Ticket", back_populates="conversation_sessions")
    conversation_turns = relationship("ConversationTurn", back_populates="session", cascade="all, delete-orphan")
    session_contexts = relationship("SessionContext", back_populates="session", cascade="all, delete-orphan")

class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)  # Sequential turn number in session
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text")  # text, voice, image, file
    ai_analysis = Column(JSON, nullable=True)  # Store AI analysis for this turn
    intent_detected = Column(String, nullable=True)
    entities_extracted = Column(JSON, nullable=True)  # Named entities, dates, etc.
    sentiment_score = Column(Float, nullable=True)
    urgency_level = Column(String, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_type = Column(String, nullable=True)  # clarification, details, confirmation, etc.
    response_effectiveness = Column(Float, nullable=True)  # User satisfaction score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ConversationSession", back_populates="conversation_turns")

class FollowUpTemplate(Base):
    __tablename__ = "follow_up_templates"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    trigger_intent = Column(String, nullable=False)  # complaint, feedback, support, etc.
    trigger_urgency = Column(String, nullable=True)  # low, medium, high, critical
    trigger_entities = Column(JSON, nullable=True)  # Required entities to trigger
    follow_up_type = Column(String, nullable=False)  # clarification, details, confirmation, resolution
    template_text = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Template variables like {user_name}, {issue_type}
    language = Column(String, default="en")
    priority = Column(Integer, default=1)  # Higher priority templates are used first
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="follow_up_templates")

class SessionContext(Base):
    __tablename__ = "session_contexts"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    context_type = Column(String, nullable=False)  # user_preferences, issue_details, resolution_status, etc.
    context_key = Column(String, nullable=False)
    context_value = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=1.0)
    source_turn = Column(Integer, nullable=True)  # Which turn this context was extracted from
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("ConversationSession", back_populates="session_contexts")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    settings_data = Column(Text, nullable=False)  # JSON string of settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmailOutreachLog(Base):
    __tablename__ = "email_outreach_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    contact_email = Column(String, nullable=False)
    email_type = Column(String, nullable=False)  # partnership, integration, custom, general
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed
    retry_count = Column(Integer, default=0)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="email_outreach_logs")

# Update existing models to include new relationships

# Add to Brand model
Brand.ai_learning_data = relationship("AILearningData", back_populates="brand")
Brand.conversation_patterns = relationship("ConversationPattern", back_populates="brand")
Brand.brand_knowledge = relationship("BrandKnowledge", back_populates="brand")
Brand.ai_response_templates = relationship("AIResponseTemplate", back_populates="brand")
Brand.user_interactions = relationship("UserInteraction", back_populates="brand")
Brand.phone_numbers = relationship("PhoneNumber", back_populates="brand")
Brand.phone_number_requests = relationship("PhoneNumberRequest", back_populates="brand")
Brand.follow_ups = relationship("FollowUpLog", back_populates="brand")
Brand.conversation_sessions = relationship("ConversationSession", back_populates="brand")
Brand.follow_up_templates = relationship("FollowUpTemplate", back_populates="brand")
Brand.email_outreach_logs = relationship("EmailOutreachLog", back_populates="brand")

# Add to Ticket model
Ticket.ai_learning_data = relationship("AILearningData", back_populates="ticket")
Ticket.crm_integrations = relationship("CRMIntegration", back_populates="ticket")
Ticket.conversation_sessions = relationship("ConversationSession", back_populates="ticket")

# Add to User model
User.interactions = relationship("UserInteraction", back_populates="user")
User.phone_number_requests = relationship("PhoneNumberRequest", back_populates="user")
User.conversation_sessions = relationship("ConversationSession", back_populates="user")