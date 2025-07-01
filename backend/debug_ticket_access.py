#!/usr/bin/env python3
"""
Debug ticket access issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Ticket, User, Brand
from sqlalchemy.orm import Session

def debug_ticket_access():
    """Debug ticket access issues"""
    db = SessionLocal()
    try:
        print("🔍 Debugging Ticket Access")
        print("=" * 50)
        
        # Get all brand users
        brand_users = db.query(User).filter(User.role.in_(['brand_user', 'admin'])).all()
        print(f"Brand users found: {len(brand_users)}")
        
        for user in brand_users:
            print(f"\n👤 User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Brand ID: {user.brand_id}")
            print(f"   Active: {user.is_active}")
            
            if user.brand_id:
                brand = db.query(Brand).filter(Brand.id == user.brand_id).first()
                if brand:
                    print(f"   Brand Name: {brand.name}")
                    
                    # Get tickets for this brand
                    brand_tickets = db.query(Ticket).filter(Ticket.brand_id == user.brand_id).all()
                    print(f"   Tickets for this brand: {len(brand_tickets)}")
                    for ticket in brand_tickets:
                        print(f"     - Ticket ID: {ticket.id}, Title: {ticket.title}, Status: {ticket.status}")
        
        print("\n" + "=" * 50)
        print("💡 To test ticket access:")
        print("1. Log in as a brand user")
        print("2. Try to access a ticket that belongs to their brand")
        print("3. Check the browser console for detailed error messages")
        
    except Exception as e:
        print(f"❌ Error debugging ticket access: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_ticket_access() 