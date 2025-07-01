from app.database import SessionLocal
from app.models import Ticket, User, TicketUrgencyEnum
from app import crud, schemas
from datetime import datetime, timedelta
import random

db = SessionLocal()
try:
    # Get the brand user
    brand_user = db.query(User).filter(User.email == "andul@gmail.com").first()
    if brand_user and brand_user.brand_id:
        print(f"Found brand user: {brand_user.email}, brand_id: {brand_user.brand_id}")
        
        # Get a user to be the owner
        owner = db.query(User).filter(User.role == "user").first()
        if not owner:
            print("No regular user found to be ticket owner")
            exit()
        
        # Create test tickets with different dates and statuses
        test_tickets = [
            {
                "title": "Product delivery delayed",
                "description": "Order was supposed to arrive yesterday but still not delivered",
                "status": "resolved",
                "category": "complaint",
                "satisfaction_rating": 4,
                "days_ago": 1
            },
            {
                "title": "Website not loading properly",
                "description": "Getting error 500 when trying to access the checkout page",
                "status": "in-progress",
                "category": "complaint",
                "satisfaction_rating": None,
                "days_ago": 2
            },
            {
                "title": "Wrong item received",
                "description": "Ordered a blue shirt but received red one",
                "status": "resolved",
                "category": "complaint",
                "satisfaction_rating": 3,
                "days_ago": 3
            },
            {
                "title": "Payment not processed",
                "description": "Credit card charge failed but order was placed",
                "status": "new",
                "category": "complaint",
                "satisfaction_rating": None,
                "days_ago": 4
            },
            {
                "title": "Customer service unresponsive",
                "description": "Called support 3 times but no one answered",
                "status": "resolved",
                "category": "complaint",
                "satisfaction_rating": 2,
                "days_ago": 5
            },
            {
                "title": "App crashes on startup",
                "description": "Mobile app immediately crashes when opened",
                "status": "in-progress",
                "category": "complaint",
                "satisfaction_rating": None,
                "days_ago": 6
            },
            {
                "title": "Refund not received",
                "description": "Returned item 2 weeks ago but refund not processed",
                "status": "resolved",
                "category": "complaint",
                "satisfaction_rating": 5,
                "days_ago": 7
            },
            {
                "title": "Account locked",
                "description": "Cannot login to account, says it's locked",
                "status": "new",
                "category": "complaint",
                "satisfaction_rating": None,
                "days_ago": 8
            }
        ]
        
        created_count = 0
        for ticket_data in test_tickets:
            # Calculate creation date
            created_date = datetime.now() - timedelta(days=ticket_data["days_ago"])
            
            ticket = Ticket(
                title=ticket_data["title"],
                description=ticket_data["description"],
                status=ticket_data["status"],
                category=ticket_data["category"],
                satisfaction_rating=ticket_data["satisfaction_rating"],
                brand_id=brand_user.brand_id,
                owner_id=owner.id,
                channel="web",
                created_at=created_date,
                urgency=TicketUrgencyEnum.medium.value
            )
            db.add(ticket)
            created_count += 1
        
        db.commit()
        print(f"Created {created_count} test tickets for analytics")
        
        # Verify the tickets
        total_tickets = db.query(Ticket).filter(Ticket.brand_id == brand_user.brand_id).count()
        resolved_tickets = db.query(Ticket).filter(
            Ticket.brand_id == brand_user.brand_id,
            Ticket.status == "resolved"
        ).count()
        
        print(f"Total tickets for brand: {total_tickets}")
        print(f"Resolved tickets: {resolved_tickets}")
        print(f"Resolution rate: {(resolved_tickets/total_tickets*100):.1f}%" if total_tickets > 0 else "No tickets")
        
    else:
        print("Brand user not found or no brand_id")
        
finally:
    db.close() 