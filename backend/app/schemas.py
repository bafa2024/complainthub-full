# backend/app/schemas.py

from pydantic import BaseModel
from typing import List, Optional
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


# -- Brand Schemas --
class BrandBase(BaseModel):
    name: str
    support_email: str
    industry: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    support_email: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None


class Brand(BrandBase):
    id: int
    credit_balance: float
    created_at: datetime

    class Config:
        orm_mode = True


# -- Ticket Schemas --
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    channel: str


class TicketCreate(TicketBase):
    brand_id: int


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatusEnum] = None
    category: Optional[TicketCategoryEnum] = None
    urgency: Optional[TicketUrgencyEnum] = None
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