import enum
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
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db.base_class import Base

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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tickets = relationship("Ticket", back_populates="brand")
    brand_users = relationship("User", back_populates="brand")

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
    brand = relationship("Brand", back_populates="brand_users")
    tickets = relationship("Ticket", foreign_keys="[Ticket.owner_id]", back_populates="owner")
    assigned_tickets = relationship("Ticket", foreign_keys="[Ticket.assignee_id]", back_populates="assignee")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(Enum(TicketStatusEnum), default=TicketStatusEnum.new)
    category = Column(Enum(TicketCategoryEnum), default=TicketCategoryEnum.complaint)
    urgency = Column(Enum(TicketUrgencyEnum), default=TicketUrgencyEnum.medium)
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
    owner = relationship("User", foreign_keys=[owner_id], back_populates="tickets")
    brand = relationship("Brand", back_populates="tickets")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tickets")