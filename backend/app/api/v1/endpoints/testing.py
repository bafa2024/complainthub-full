from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Brand, Ticket, RoleEnum, TicketStatusEnum, TicketCategoryEnum, TicketUrgencyEnum
from app.schemas import UserCreate, BrandCreate, TicketCreate
from datetime import datetime
import json
from typing import Dict, Any, List

router = APIRouter()

@router.get("/")
def testing_dashboard():
    """Main testing dashboard with links to all test endpoints"""
    return {
        "message": "Testing Dashboard",
        "description": "Comprehensive testing endpoints for developers",
        "endpoints": {
            "database_tests": "/api/v1/testing/database",
            "api_connectivity_tests": "/api/v1/testing/api",
            "data_flow_tests": "/api/v1/testing/data-flow",
            "crud_tests": "/api/v1/testing/crud",
            "mock_data_tests": "/api/v1/testing/mock-data",
            "health_check": "/api/v1/testing/health"
        },
        "usage": "Visit each endpoint to run specific tests and see results"
    }

@router.get("/health")
def testing_health_check():
    """Basic health check for testing infrastructure"""
    return {
        "status": "healthy",
        "testing_infrastructure": "active",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/database")
def test_database_connection(db: Session = Depends(get_db)):
    """Test database connection and basic operations"""
    results = {
        "database_connection": "unknown",
        "tables_exist": "unknown",
        "can_query": "unknown",
        "can_insert": "unknown",
        "can_update": "unknown",
        "can_delete": "unknown",
        "errors": []
    }
    
    try:
        # Test basic connection
        db.execute(text("SELECT 1"))
        results["database_connection"] = "success"
        
        # Test if tables exist
        tables = ["users", "brands", "tickets"]
        existing_tables = []
        for table in tables:
            try:
                db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                existing_tables.append(table)
            except Exception as e:
                results["errors"].append(f"Table {table} not found: {str(e)}")
        
        results["tables_exist"] = f"Found tables: {existing_tables}"
        
        # Test basic query
        user_count = db.query(User).count()
        results["can_query"] = f"success - {user_count} users found"
        
        # Test insert (create a test user)
        test_user = User(
            email="test@testing.com",
            hashed_password="test_hash",
            full_name="Test User",
            role=RoleEnum.user
        )
        db.add(test_user)
        db.commit()
        results["can_insert"] = "success"
        
        # Test update
        test_user.full_name = "Updated Test User"
        db.commit()
        results["can_update"] = "success"
        
        # Test delete
        db.delete(test_user)
        db.commit()
        results["can_delete"] = "success"
        
    except Exception as e:
        results["errors"].append(f"Database test failed: {str(e)}")
        db.rollback()
    
    return results

@router.get("/api")
def test_api_connectivity():
    """Test API connectivity and response times"""
    import time
    import requests
    
    results = {
        "api_accessible": "unknown",
        "response_time": "unknown",
        "cors_enabled": "unknown",
        "endpoints_working": {},
        "errors": []
    }
    
    try:
        # Test if API is accessible
        start_time = time.time()
        response = requests.get("http://localhost:8000/health", timeout=5)
        end_time = time.time()
        
        results["api_accessible"] = "success" if response.status_code == 200 else "failed"
        results["response_time"] = f"{(end_time - start_time) * 1000:.2f}ms"
        
        # Test CORS
        cors_response = requests.options("http://localhost:8000/health")
        results["cors_enabled"] = "success" if "access-control-allow-origin" in cors_response.headers else "failed"
        
        # Test various endpoints
        endpoints = [
            "/api/v1/test",
            "/api/v1/users",
            "/api/v1/brands",
            "/api/v1/tickets"
        ]
        
        for endpoint in endpoints:
            try:
                resp = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                results["endpoints_working"][endpoint] = resp.status_code
            except Exception as e:
                results["endpoints_working"][endpoint] = f"error: {str(e)}"
                
    except Exception as e:
        results["errors"].append(f"API connectivity test failed: {str(e)}")
    
    return results

@router.get("/data-flow")
def test_data_flow(db: Session = Depends(get_db)):
    """Test complete data flow from frontend to backend"""
    results = {
        "user_creation_flow": "unknown",
        "brand_creation_flow": "unknown",
        "ticket_creation_flow": "unknown",
        "data_retrieval_flow": "unknown",
        "test_data": {},
        "errors": []
    }
    
    try:
        # Test user creation flow
        test_user_data = {
            "email": "flowtest@example.com",
            "password": "testpass123",
            "full_name": "Flow Test User",
            "phone_number": "+1234567890"
        }
        
        # Simulate user creation
        test_user = User(
            email=test_user_data["email"],
            hashed_password="hashed_" + test_user_data["password"],
            full_name=test_user_data["full_name"],
            phone_number=test_user_data["phone_number"],
            role=RoleEnum.user
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        results["user_creation_flow"] = "success"
        results["test_data"]["user_id"] = test_user.id
        
        # Test brand creation flow
        test_brand_data = {
            "name": "Flow Test Brand",
            "support_email": "support@flowtestbrand.com",
            "industry": "Technology"
        }
        
        test_brand = Brand(
            name=test_brand_data["name"],
            support_email=test_brand_data["support_email"],
            industry=test_brand_data["industry"]
        )
        db.add(test_brand)
        db.commit()
        db.refresh(test_brand)
        
        results["brand_creation_flow"] = "success"
        results["test_data"]["brand_id"] = test_brand.id
        
        # Test ticket creation flow
        test_ticket_data = {
            "title": "Flow Test Ticket",
            "description": "Testing data flow from frontend to backend",
            "category": TicketCategoryEnum.complaint,
            "urgency": TicketUrgencyEnum.medium,
            "channel": "web"
        }
        
        test_ticket = Ticket(
            title=test_ticket_data["title"],
            description=test_ticket_data["description"],
            category=test_ticket_data["category"],
            urgency=test_ticket_data["urgency"],
            channel=test_ticket_data["channel"],
            owner_id=test_user.id,
            brand_id=test_brand.id
        )
        db.add(test_ticket)
        db.commit()
        db.refresh(test_ticket)
        
        results["ticket_creation_flow"] = "success"
        results["test_data"]["ticket_id"] = test_ticket.id
        
        # Test data retrieval flow
        retrieved_user = db.query(User).filter(User.id == test_user.id).first()
        retrieved_brand = db.query(Brand).filter(Brand.id == test_brand.id).first()
        retrieved_ticket = db.query(Ticket).filter(Ticket.id == test_ticket.id).first()
        
        if all([retrieved_user, retrieved_brand, retrieved_ticket]):
            results["data_retrieval_flow"] = "success"
        else:
            results["data_retrieval_flow"] = "failed"
        
        # Clean up test data
        db.delete(test_ticket)
        db.delete(test_brand)
        db.delete(test_user)
        db.commit()
        
    except Exception as e:
        results["errors"].append(f"Data flow test failed: {str(e)}")
        db.rollback()
    
    return results

@router.get("/crud")
def test_crud_operations(db: Session = Depends(get_db)):
    """Test CRUD operations for all models"""
    results = {
        "user_crud": {},
        "brand_crud": {},
        "ticket_crud": {},
        "errors": []
    }
    
    try:
        # Test User CRUD
        # Create
        user = User(
            email="crudtest@example.com",
            hashed_password="test_hash",
            full_name="CRUD Test User",
            role=RoleEnum.user
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        results["user_crud"]["create"] = f"success - ID: {user.id}"
        
        # Read
        retrieved_user = db.query(User).filter(User.id == user.id).first()
        results["user_crud"]["read"] = "success" if retrieved_user else "failed"
        
        # Update
        user.full_name = "Updated CRUD User"
        db.commit()
        results["user_crud"]["update"] = "success"
        
        # Delete
        db.delete(user)
        db.commit()
        results["user_crud"]["delete"] = "success"
        
        # Test Brand CRUD
        brand = Brand(
            name="CRUD Test Brand",
            support_email="support@crudtest.com"
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
        results["brand_crud"]["create"] = f"success - ID: {brand.id}"
        
        retrieved_brand = db.query(Brand).filter(Brand.id == brand.id).first()
        results["brand_crud"]["read"] = "success" if retrieved_brand else "failed"
        
        brand.name = "Updated CRUD Brand"
        db.commit()
        results["brand_crud"]["update"] = "success"
        
        db.delete(brand)
        db.commit()
        results["brand_crud"]["delete"] = "success"
        
        # Test Ticket CRUD
        # Need a user and brand for ticket
        temp_user = User(
            email="temp@crud.com",
            hashed_password="temp_hash",
            full_name="Temp User",
            role=RoleEnum.user
        )
        temp_brand = Brand(
            name="Temp Brand",
            support_email="temp@brand.com"
        )
        db.add_all([temp_user, temp_brand])
        db.commit()
        
        ticket = Ticket(
            title="CRUD Test Ticket",
            description="Testing CRUD operations",
            status=TicketStatusEnum.new,
            category=TicketCategoryEnum.complaint,
            urgency=TicketUrgencyEnum.medium,
            owner_id=temp_user.id,
            brand_id=temp_brand.id,
            channel="web"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        results["ticket_crud"]["create"] = f"success - ID: {ticket.id}"
        
        retrieved_ticket = db.query(Ticket).filter(Ticket.id == ticket.id).first()
        results["ticket_crud"]["read"] = "success" if retrieved_ticket else "failed"
        
        ticket.title = "Updated CRUD Ticket"
        db.commit()
        results["ticket_crud"]["update"] = "success"
        
        # Clean up
        db.delete(ticket)
        db.delete(temp_user)
        db.delete(temp_brand)
        db.commit()
        results["ticket_crud"]["delete"] = "success"
        
    except Exception as e:
        results["errors"].append(f"CRUD test failed: {str(e)}")
        db.rollback()
    
    return results

@router.get("/mock-data")
def test_mock_data_generation(db: Session = Depends(get_db)):
    """Test mock data generation and validation"""
    results = {
        "mock_users_created": 0,
        "mock_brands_created": 0,
        "mock_tickets_created": 0,
        "data_validation": {},
        "errors": []
    }
    
    try:
        # Create mock users
        mock_users = []
        for i in range(3):
            user = User(
                email=f"mockuser{i}@example.com",
                hashed_password=f"mock_hash_{i}",
                full_name=f"Mock User {i}",
                phone_number=f"+123456789{i}",
                role=RoleEnum.user
            )
            mock_users.append(user)
        
        db.add_all(mock_users)
        db.commit()
        results["mock_users_created"] = len(mock_users)
        
        # Create mock brands
        mock_brands = []
        for i in range(2):
            brand = Brand(
                name=f"Mock Brand {i}",
                support_email=f"support@mockbrand{i}.com",
                industry=f"Industry {i}",
                credit_balance=1000.0
            )
            mock_brands.append(brand)
        
        db.add_all(mock_brands)
        db.commit()
        results["mock_brands_created"] = len(mock_brands)
        
        # Create mock tickets
        mock_tickets = []
        for i in range(5):
            ticket = Ticket(
                title=f"Mock Ticket {i}",
                description=f"This is mock ticket {i} for testing purposes",
                status=TicketStatusEnum.new,
                category=TicketCategoryEnum.complaint,
                urgency=TicketUrgencyEnum.medium,
                abuse_level_flag=False,
                channel="web",
                owner_id=mock_users[i % len(mock_users)].id,
                brand_id=mock_brands[i % len(mock_brands)].id,
                is_public=False
            )
            mock_tickets.append(ticket)
        
        db.add_all(mock_tickets)
        db.commit()
        results["mock_tickets_created"] = len(mock_tickets)
        
        # Validate data
        total_users = db.query(User).count()
        total_brands = db.query(Brand).count()
        total_tickets = db.query(Ticket).count()
        
        results["data_validation"] = {
            "total_users_in_db": total_users,
            "total_brands_in_db": total_brands,
            "total_tickets_in_db": total_tickets,
            "mock_data_percentage": {
                "users": f"{(len(mock_users) / total_users * 100):.1f}%" if total_users > 0 else "0%",
                "brands": f"{(len(mock_brands) / total_brands * 100):.1f}%" if total_brands > 0 else "0%",
                "tickets": f"{(len(mock_tickets) / total_tickets * 100):.1f}%" if total_tickets > 0 else "0%"
            }
        }
        
        # Clean up mock data
        db.query(Ticket).filter(Ticket.id.in_([t.id for t in mock_tickets])).delete()
        db.query(Brand).filter(Brand.id.in_([b.id for b in mock_brands])).delete()
        db.query(User).filter(User.id.in_([u.id for u in mock_users])).delete()
        db.commit()
        
    except Exception as e:
        results["errors"].append(f"Mock data test failed: {str(e)}")
        db.rollback()
    
    return results 