from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, index=True)
    user_identifier = Column(String, index=True)
    content = Column(Text)
    sentiment = Column(Float)
    severity = Column(Integer)
    status = Column(String, default='open')
    created_at = Column(DateTime, default=datetime.utcnow)
