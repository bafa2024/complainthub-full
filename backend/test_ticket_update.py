#!/usr/bin/env python3
"""
Test ticket update functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Ticket, User, TicketStatusEnum
from app.schemas import TicketUpdate
from app import crud
from sqlalchemy.orm import Session

def test_ticket_update():
    """Test ticket update functionality"""
    db = SessionLocal()
    try:
        print("🧪 Testing Ticket Update Functionality")
        print("=" * 50)
        
        # Get a test ticket
        ticket = db.query(Ticket).first()
        if not ticket:
            print("❌ No tickets found in database!")
            return
        
        print(f"Testing with ticket ID: {ticket.id}")
        print(f"Current status: {ticket.status}")
        print(f"Brand ID: {ticket.brand_id}")
        
        # Test updating status to 'in-progress'
        update_data = TicketUpdate(status=TicketStatusEnum.in_progress)
        print(f"Update data: {update_data.dict()}")
        
        try:
            updated_ticket = crud.update_ticket(db, ticket.id, update_data)
            if updated_ticket:
                print(f"✅ Ticket updated successfully!")
                print(f"New status: {updated_ticket.status}")
            else:
                print("❌ Ticket update returned None")
        except Exception as e:
            print(f"❌ Error updating ticket: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_ticket_update() 