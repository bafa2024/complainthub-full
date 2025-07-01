#!/usr/bin/env python3
"""
Check tickets in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Ticket, User, Brand
from sqlalchemy.orm import Session

def check_tickets():
    """Check tickets in the database"""
    db = SessionLocal()
    try:
        print("🔍 Checking tickets in database...")
        print("=" * 50)
        
        # Check if there are any tickets
        tickets = db.query(Ticket).all()
        print(f"Total tickets found: {len(tickets)}")
        
        if tickets:
            print("\n📋 Ticket Details:")
            for ticket in tickets:
                print(f"ID: {ticket.id}")
                print(f"Title: {ticket.title}")
                print(f"Status: {ticket.status}")
                print(f"Brand ID: {ticket.brand_id}")
                print(f"Owner ID: {ticket.owner_id}")
                print(f"Created: {ticket.created_at}")
                print("-" * 30)
        else:
            print("\n❌ No tickets found in database!")
            print("You need to create some tickets first.")
            
            # Check if there are users and brands
            users = db.query(User).all()
            brands = db.query(Brand).all()
            print(f"\nUsers found: {len(users)}")
            print(f"Brands found: {len(brands)}")
            
            if users and brands:
                print("\n💡 To create a test ticket, you can:")
                print("1. Use the frontend to create a complaint")
                print("2. Or run the test script: python test_models.py")
        
    except Exception as e:
        print(f"❌ Error checking tickets: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tickets() 