#!/usr/bin/env python3
"""
Check SQLite database and add test data if needed
"""

import sqlite3
import os

DB_PATH = "backend/voicebot.db"

def check_database():
    """Check the database and add test data if needed"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📋 Found {len(tables)} tables: {[table[0] for table in tables]}")
    
    # Check brands
    cursor.execute("SELECT COUNT(*) FROM brands")
    brand_count = cursor.fetchone()[0]
    print(f"🏢 Brands in database: {brand_count}")
    
    if brand_count == 0:
        print("➕ Adding test brands...")
        test_brands = [
            ("Acme Corporation", "support@acme.com", "Technology"),
            ("ShopEasy", "help@shopeasy.com", "Retail"),
            ("GadgetPro", "support@gadgetpro.com", "Electronics"),
            ("FoodExpress", "customer@foodexpress.com", "Food & Beverage"),
            ("TravelWise", "support@travelwise.com", "Travel")
        ]
        
        for name, email, industry in test_brands:
            cursor.execute("""
                INSERT INTO brands (name, support_email, industry, credit_balance, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (name, email, industry, 1000.0))
        
        conn.commit()
        print(f"✅ Added {len(test_brands)} test brands")
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"👥 Users in database: {user_count}")
    
    # Check tickets
    cursor.execute("SELECT COUNT(*) FROM tickets")
    ticket_count = cursor.fetchone()[0]
    print(f"🎫 Tickets in database: {ticket_count}")
    
    # Show some sample data
    print("\n📊 Sample Data:")
    
    cursor.execute("SELECT id, name, support_email FROM brands LIMIT 3")
    brands = cursor.fetchall()
    print("🏢 Sample Brands:")
    for brand in brands:
        print(f"  - {brand[1]} ({brand[2]})")
    
    cursor.execute("SELECT id, email, full_name, role FROM users LIMIT 3")
    users = cursor.fetchall()
    print("👥 Sample Users:")
    for user in users:
        print(f"  - {user[2]} ({user[1]}) - {user[3]}")
    
    if ticket_count > 0:
        cursor.execute("""
            SELECT t.id, t.title, t.status, b.name as brand_name, u.full_name as user_name
            FROM tickets t
            LEFT JOIN brands b ON t.brand_id = b.id
            LEFT JOIN users u ON t.owner_id = u.id
            LIMIT 3
        """)
        tickets = cursor.fetchall()
        print("🎫 Sample Tickets:")
        for ticket in tickets:
            print(f"  - {ticket[1]} (Status: {ticket[2]}, Brand: {ticket[3]}, User: {ticket[4]})")
    
    conn.close()
    print("\n✅ Database check complete!")

if __name__ == "__main__":
    check_database() 