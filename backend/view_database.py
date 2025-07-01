#!/usr/bin/env python3
"""
Database Viewer for ComplaintHub
Run this script to view data in your PostgreSQL database
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, text
from tabulate import tabulate
import psycopg2
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Ticket, User, Brand

# Load environment variables
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost/complaintdb")

def view_users():
    """View all users in the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get users
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                email,
                phone,
                is_active,
                is_brand,
                is_admin,
                created_at
            FROM users
            ORDER BY created_at DESC
        """))
        
        users = result.fetchall()
        
        if users:
            # Convert to list of lists for tabulate
            user_data = []
            for user in users:
                user_data.append([
                    user[0],  # id
                    user[1],  # name
                    user[2],  # email
                    user[3],  # phone
                    "✓" if user[4] else "✗",  # is_active
                    "✓" if user[5] else "✗",  # is_brand
                    "✓" if user[6] else "✗",  # is_admin
                    user[7].strftime("%Y-%m-%d %H:%M") if user[7] else "N/A"  # created_at
                ])
            
            print("\n=== REGISTERED USERS ===")
            print(tabulate(
                user_data,
                headers=["ID", "Name", "Email", "Phone", "Active", "Brand", "Admin", "Created"],
                tablefmt="grid"
            ))
            print(f"\nTotal users: {len(users)}")
        else:
            print("\nNo users found in the database.")

def view_brands():
    """View all brands in the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                email,
                support_email,
                phone_number,
                credit_balance,
                created_at
            FROM brands
            ORDER BY created_at DESC
        """))
        
        brands = result.fetchall()
        
        if brands:
            brand_data = []
            for brand in brands:
                brand_data.append([
                    brand[0],  # id
                    brand[1],  # name
                    brand[2],  # email
                    brand[3] or "N/A",  # support_email
                    brand[4] or "N/A",  # phone_number
                    f"₹{brand[5]:.2f}" if brand[5] else "₹0.00",  # credit_balance
                    brand[6].strftime("%Y-%m-%d %H:%M") if brand[6] else "N/A"  # created_at
                ])
            
            print("\n=== REGISTERED BRANDS ===")
            print(tabulate(
                brand_data,
                headers=["ID", "Name", "Email", "Support Email", "Phone", "Credits", "Created"],
                tablefmt="grid"
            ))
            print(f"\nTotal brands: {len(brands)}")
        else:
            print("\nNo brands found in the database.")

def view_tickets():
    """View all tickets in the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                t.id,
                u.name as user_name,
                b.name as brand_name,
                t.channel,
                t.category,
                t.status,
                t.urgency,
                LEFT(t.description, 50) as description,
                t.created_at
            FROM tickets t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN brands b ON t.brand_id = b.id
            ORDER BY t.created_at DESC
            LIMIT 20
        """))
        
        tickets = result.fetchall()
        
        if tickets:
            ticket_data = []
            for ticket in tickets:
                ticket_data.append([
                    ticket[0],  # id
                    ticket[1] or "Anonymous",  # user_name
                    ticket[2] or "N/A",  # brand_name
                    ticket[3],  # channel
                    ticket[4],  # category
                    ticket[5],  # status
                    ticket[6],  # urgency
                    ticket[7] + "..." if ticket[7] else "N/A",  # description
                    ticket[8].strftime("%Y-%m-%d %H:%M") if ticket[8] else "N/A"  # created_at
                ])
            
            print("\n=== RECENT TICKETS (Last 20) ===")
            print(tabulate(
                ticket_data,
                headers=["ID", "User", "Brand", "Channel", "Category", "Status", "Urgency", "Description", "Created"],
                tablefmt="grid"
            ))
            print(f"\nShowing last 20 tickets")
        else:
            print("\nNo tickets found in the database.")

def view_database_stats():
    """View overall database statistics"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get counts
        user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        brand_count = conn.execute(text("SELECT COUNT(*) FROM brands")).scalar()
        ticket_count = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
        
        # Get ticket stats
        ticket_stats = conn.execute(text("""
            SELECT 
                status,
                COUNT(*) as count
            FROM tickets
            GROUP BY status
        """)).fetchall()
        
        print("\n=== DATABASE STATISTICS ===")
        print(f"Total Users: {user_count}")
        print(f"Total Brands: {brand_count}")
        print(f"Total Tickets: {ticket_count}")
        
        if ticket_stats:
            print("\nTickets by Status:")
            for stat in ticket_stats:
                print(f"  - {stat[0]}: {stat[1]}")

def test_connection():
    """Test database connection"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Main function to run the viewer"""
    print("ComplaintHub Database Viewer")
    print("=" * 50)
    
    if not test_connection():
        return
    
    while True:
        print("\nWhat would you like to view?")
        print("1. Users")
        print("2. Brands")
        print("3. Tickets")
        print("4. Database Statistics")
        print("5. All of the above")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_users()
        elif choice == "2":
            view_brands()
        elif choice == "3":
            view_tickets()
        elif choice == "4":
            view_database_stats()
        elif choice == "5":
            view_database_stats()
            view_users()
            view_brands()
            view_tickets()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

print('--- All Brands ---')
db = SessionLocal()
brands = db.query(Brand).all()
for b in brands:
    print(f'Brand ID: {b.id}, Name: {b.name}')

print('\n--- All Brand Users ---')
users = db.query(User).filter(User.role == 'brand_user').all()
for u in users:
    print(f'User ID: {u.id}, Email: {u.email}, Brand ID: {u.brand_id}')

print('\n--- All Tickets ---')
tickets = db.query(Ticket).all()
for t in tickets:
    print(f'Ticket ID: {t.id}, Title: {t.title}, Brand ID: {t.brand_id}, Status: {t.status}')

def assign_brand_to_user(user_email, brand_id):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        print(f'User {user_email} not found!')
        return
    user.brand_id = brand_id
    db.commit()
    print(f'Assigned brand_id {brand_id} to user {user_email}')

# Example usage:
# assign_brand_to_user("testbrand@example.com", 1)

db.close()