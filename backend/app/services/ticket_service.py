# backend/app/services/ticket_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime

from app.models import Ticket, User, Brand, ConversationSession
from app.core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class TicketService:
    """Service for managing ticket operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
    
    def create_ticket(
        self,
        title: str,
        description: str,
        category: str = "complaint",
        urgency: str = "medium",
        user_id: int = None,
        brand_id: int = None,
        language: str = "en",
        channel: str = "web",
        metadata: Dict[str, Any] = None
    ) -> Ticket:
        """Create a new ticket with AI analysis"""
        try:
            # Create ticket object
            ticket = Ticket(
                title=title,
                description=description,
                category=category,
                urgency=urgency,
                user_id=user_id,
                brand_id=brand_id,
                language=language,
                channel=channel,
                status="open",
                metadata=json.dumps(metadata or {}),
                created_at=datetime.utcnow()
            )
            
            # Add to database
            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)
            
            logger.info(f"Created ticket {ticket.id} for user {user_id} and brand {brand_id}")
            
            # Log ticket creation for analytics
            self._log_ticket_event(ticket.id, "created", metadata)
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            self.db.rollback()
            raise
    
    def update_ticket_status(
        self,
        ticket_id: int,
        status: str,
        user_id: int = None,
        notes: str = None
    ) -> Optional[Ticket]:
        """Update ticket status"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return None
            
            old_status = ticket.status
            ticket.status = status
            ticket.updated_at = datetime.utcnow()
            
            # Add status change to metadata
            if ticket.metadata:
                metadata = json.loads(ticket.metadata)
            else:
                metadata = {}
            
            if "status_history" not in metadata:
                metadata["status_history"] = []
            
            metadata["status_history"].append({
                "from_status": old_status,
                "to_status": status,
                "changed_by": user_id,
                "changed_at": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            ticket.metadata = json.dumps(metadata)
            
            self.db.commit()
            self.db.refresh(ticket)
            
            logger.info(f"Updated ticket {ticket_id} status from {old_status} to {status}")
            
            # Log status change
            self._log_ticket_event(ticket_id, "status_changed", {
                "from_status": old_status,
                "to_status": status,
                "changed_by": user_id
            })
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            self.db.rollback()
            raise
    
    def get_ticket(self, ticket_id: int, user_id: int = None, brand_id: int = None) -> Optional[Ticket]:
        """Get ticket with access control"""
        try:
            query = self.db.query(Ticket).filter(Ticket.id == ticket_id)
            
            # Apply access control
            if user_id:
                query = query.filter(
                    or_(
                        Ticket.user_id == user_id,
                        Ticket.brand_id.in_(
                            self.db.query(Brand.id).filter(Brand.user_id == user_id)
                        )
                    )
                )
            elif brand_id:
                query = query.filter(Ticket.brand_id == brand_id)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return None
    
    def get_tickets_for_user(
        self,
        user_id: int,
        status: str = None,
        category: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        """Get tickets for a user"""
        try:
            query = self.db.query(Ticket).filter(Ticket.user_id == user_id)
            
            if status:
                query = query.filter(Ticket.status == status)
            
            if category:
                query = query.filter(Ticket.category == category)
            
            return query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting tickets for user {user_id}: {e}")
            return []
    
    def get_tickets_for_brand(
        self,
        brand_id: int,
        status: str = None,
        category: str = None,
        urgency: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        """Get tickets for a brand"""
        try:
            query = self.db.query(Ticket).filter(Ticket.brand_id == brand_id)
            
            if status:
                query = query.filter(Ticket.status == status)
            
            if category:
                query = query.filter(Ticket.category == category)
            
            if urgency:
                query = query.filter(Ticket.urgency == urgency)
            
            return query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting tickets for brand {brand_id}: {e}")
            return []
    
    def search_tickets(
        self,
        search_query: str,
        user_id: int = None,
        brand_id: int = None,
        limit: int = 20
    ) -> List[Ticket]:
        """Search tickets by title and description"""
        try:
            query = self.db.query(Ticket)
            
            # Apply search filter
            search_filter = or_(
                Ticket.title.contains(search_query),
                Ticket.description.contains(search_query)
            )
            query = query.filter(search_filter)
            
            # Apply access control
            if user_id:
                query = query.filter(Ticket.user_id == user_id)
            elif brand_id:
                query = query.filter(Ticket.brand_id == brand_id)
            
            return query.order_by(Ticket.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching tickets: {e}")
            return []
    
    def get_ticket_stats(self, brand_id: int = None, user_id: int = None) -> Dict[str, Any]:
        """Get ticket statistics"""
        try:
            base_query = self.db.query(Ticket)
            
            if brand_id:
                base_query = base_query.filter(Ticket.brand_id == brand_id)
            elif user_id:
                base_query = base_query.filter(Ticket.user_id == user_id)
            
            total_tickets = base_query.count()
            open_tickets = base_query.filter(Ticket.status == "open").count()
            in_progress_tickets = base_query.filter(Ticket.status == "in_progress").count()
            resolved_tickets = base_query.filter(Ticket.status == "resolved").count()
            closed_tickets = base_query.filter(Ticket.status == "closed").count()
            
            # Category breakdown
            category_stats = {}
            categories = self.db.query(Ticket.category).filter(
                base_query.statement.whereclause
            ).distinct().all()
            
            for (category,) in categories:
                if category:
                    count = base_query.filter(Ticket.category == category).count()
                    category_stats[category] = count
            
            # Urgency breakdown
            urgency_stats = {}
            urgencies = ["low", "medium", "high", "critical"]
            for urgency in urgencies:
                count = base_query.filter(Ticket.urgency == urgency).count()
                if count > 0:
                    urgency_stats[urgency] = count
            
            return {
                "total": total_tickets,
                "open": open_tickets,
                "in_progress": in_progress_tickets,
                "resolved": resolved_tickets,
                "closed": closed_tickets,
                "by_category": category_stats,
                "by_urgency": urgency_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket stats: {e}")
            return {
                "total": 0,
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
                "closed": 0,
                "by_category": {},
                "by_urgency": {}
            }
    
    def assign_ticket(self, ticket_id: int, assigned_to_id: int, assigned_by_id: int) -> Optional[Ticket]:
        """Assign ticket to a user"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return None
            
            old_assignee = ticket.assigned_to_id
            ticket.assigned_to_id = assigned_to_id
            ticket.updated_at = datetime.utcnow()
            
            # Update metadata
            if ticket.metadata:
                metadata = json.loads(ticket.metadata)
            else:
                metadata = {}
            
            if "assignment_history" not in metadata:
                metadata["assignment_history"] = []
            
            metadata["assignment_history"].append({
                "from_assignee": old_assignee,
                "to_assignee": assigned_to_id,
                "assigned_by": assigned_by_id,
                "assigned_at": datetime.utcnow().isoformat()
            })
            
            ticket.metadata = json.dumps(metadata)
            
            self.db.commit()
            self.db.refresh(ticket)
            
            logger.info(f"Assigned ticket {ticket_id} to user {assigned_to_id}")
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error assigning ticket: {e}")
            self.db.rollback()
            raise
    
    def add_ticket_note(
        self,
        ticket_id: int,
        note: str,
        user_id: int,
        note_type: str = "internal"
    ) -> bool:
        """Add a note to a ticket"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return False
            
            # Update metadata with note
            if ticket.metadata:
                metadata = json.loads(ticket.metadata)
            else:
                metadata = {}
            
            if "notes" not in metadata:
                metadata["notes"] = []
            
            metadata["notes"].append({
                "note": note,
                "type": note_type,
                "author_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            })
            
            ticket.metadata = json.dumps(metadata)
            ticket.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Added note to ticket {ticket_id} by user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding ticket note: {e}")
            self.db.rollback()
            return False
    
    def _log_ticket_event(self, ticket_id: int, event_type: str, metadata: Dict[str, Any] = None):
        """Log ticket events for analytics"""
        try:
            # This would typically go to a separate analytics/logging service
            # For now, just log it
            logger.info(f"Ticket event: {event_type} for ticket {ticket_id}", extra={
                "ticket_id": ticket_id,
                "event_type": event_type,
                "metadata": metadata
            })
            
        except Exception as e:
            logger.error(f"Error logging ticket event: {e}")