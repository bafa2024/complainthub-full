#!/usr/bin/env python3
"""
Advanced Billing & Payment Integration Test Script
==================================================

This script tests the comprehensive billing system including:
- Credit top-up payments
- Subscription management
- Complaint charge processing
- Transaction history
- Billing analytics
- Admin billing management
- Stripe webhook handling
- Invoice generation
- Refund processing

Usage:
    python test_billing_system.py

Requirements:
    - Backend server running on http://localhost:8000
    - Valid admin and brand user credentials
    - Stripe test keys configured
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (update with your actual test users)
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"
}

BRAND_CREDENTIALS = {
    "email": "brand@test.com", 
    "password": "brand123"
}

class BillingSystemTester:
    def __init__(self):
        self.admin_token = None
        self.brand_token = None
        self.test_brand_id = None
        self.test_transaction_id = None
        self.test_subscription_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def login_admin(self) -> bool:
        """Login as admin user"""
        try:
            self.log("Logging in as admin...")
            response = requests.post(f"{API_BASE}/login/access-token", data=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("Admin login successful")
                return True
            else:
                self.log(f"Admin login failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Admin login error: {e}", "ERROR")
            return False
    
    def login_brand(self) -> bool:
        """Login as brand user"""
        try:
            self.log("Logging in as brand user...")
            response = requests.post(f"{API_BASE}/login/access-token", data=BRAND_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.brand_token = data.get("access_token")
                
                # Get brand ID
                headers = {"Authorization": f"Bearer {self.brand_token}"}
                user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    self.test_brand_id = user_data.get("brand_id")
                
                self.log("Brand login successful")
                return True
            else:
                self.log(f"Brand login failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Brand login error: {e}", "ERROR")
            return False
    
    def test_billing_summary(self) -> bool:
        """Test getting billing summary"""
        try:
            self.log("Testing billing summary...")
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            response = requests.get(f"{API_BASE}/billing/summary", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Billing summary retrieved: Balance ₹{data.get('current_balance', 0)}")
                return True
            else:
                self.log(f"Billing summary failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Billing summary error: {e}", "ERROR")
            return False
    
    def test_transaction_history(self) -> bool:
        """Test getting transaction history"""
        try:
            self.log("Testing transaction history...")
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            response = requests.get(f"{API_BASE}/billing/transactions?limit=10", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                self.log(f"Transaction history retrieved: {len(transactions)} transactions")
                
                if transactions:
                    self.test_transaction_id = transactions[0]["id"]
                
                return True
            else:
                self.log(f"Transaction history failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Transaction history error: {e}", "ERROR")
            return False
    
    def test_subscription_plans(self) -> bool:
        """Test getting subscription plans"""
        try:
            self.log("Testing subscription plans...")
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            response = requests.get(f"{API_BASE}/billing/plans", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                plans = data.get("plans", {})
                self.log(f"Subscription plans retrieved: {len(plans)} plans available")
                
                for plan_name, plan_data in plans.items():
                    self.log(f"  - {plan_name}: ₹{plan_data.get('price')}/month")
                
                return True
            else:
                self.log(f"Subscription plans failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Subscription plans error: {e}", "ERROR")
            return False
    
    def test_billing_analytics(self) -> bool:
        """Test getting billing analytics"""
        try:
            self.log("Testing billing analytics...")
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            response = requests.get(f"{API_BASE}/billing/analytics?date_range=30d", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", {})
                self.log(f"Billing analytics retrieved:")
                self.log(f"  - Total spent: ₹{summary.get('total_spent', 0)}")
                self.log(f"  - Total credits added: ₹{summary.get('total_credits_added', 0)}")
                self.log(f"  - Total charges: ₹{summary.get('total_charges', 0)}")
                self.log(f"  - Transaction count: {summary.get('transaction_count', 0)}")
                return True
            else:
                self.log(f"Billing analytics failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Billing analytics error: {e}", "ERROR")
            return False
    
    def test_credit_topup_creation(self) -> bool:
        """Test creating credit top-up (without actual payment)"""
        try:
            self.log("Testing credit top-up creation...")
            headers = {
                "Authorization": f"Bearer {self.brand_token}",
                "Content-Type": "application/json"
            }
            
            # Test with a small amount
            topup_data = {
                "amount": 100,
                "payment_method": "stripe"
            }
            
            response = requests.post(f"{API_BASE}/billing/topup", 
                                   json=topup_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Credit top-up created: Payment Intent {data.get('payment_intent_id')}")
                return True
            else:
                self.log(f"Credit top-up creation failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Credit top-up creation error: {e}", "ERROR")
            return False
    
    def test_invoice_generation(self) -> bool:
        """Test invoice generation"""
        if not self.test_transaction_id:
            self.log("No transaction ID available for invoice test", "WARNING")
            return True
            
        try:
            self.log("Testing invoice generation...")
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            response = requests.get(f"{API_BASE}/billing/invoice/{self.test_transaction_id}", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Invoice generated: {data.get('invoice_number')}")
                return True
            else:
                self.log(f"Invoice generation failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Invoice generation error: {e}", "ERROR")
            return False
    
    def test_admin_billing_logs(self) -> bool:
        """Test admin billing logs access"""
        try:
            self.log("Testing admin billing logs...")
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_BASE}/billing/admin/billing-logs?limit=10", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Admin billing logs retrieved: {len(data.get('transactions', []))} transactions")
                return True
            else:
                self.log(f"Admin billing logs failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Admin billing logs error: {e}", "ERROR")
            return False
    
    def test_refund_processing(self) -> bool:
        """Test refund processing (admin only)"""
        if not self.test_transaction_id:
            self.log("No transaction ID available for refund test", "WARNING")
            return True
            
        try:
            self.log("Testing refund processing...")
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            refund_data = {
                "reason": "Test refund for billing system testing"
            }
            
            response = requests.post(f"{API_BASE}/billing/refund/{self.test_transaction_id}", 
                                   json=refund_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Refund processed: {data.get('refund_id')}")
                return True
            else:
                self.log(f"Refund processing failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Refund processing error: {e}", "ERROR")
            return False
    
    def test_complaint_charge_processing(self) -> bool:
        """Test complaint charge processing"""
        try:
            self.log("Testing complaint charge processing...")
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, create a test ticket
            ticket_data = {
                "title": "Test complaint for billing",
                "description": "This is a test complaint to test billing charges",
                "brand_id": self.test_brand_id,
                "category": "complaint",
                "urgency": "medium"
            }
            
            ticket_response = requests.post(f"{API_BASE}/tickets", 
                                          json=ticket_data, headers=headers)
            
            if ticket_response.status_code == 200:
                ticket_id = ticket_response.json().get("id")
                self.log(f"Test ticket created: {ticket_id}")
                
                # Now test complaint charge processing
                charge_response = requests.post(f"{API_BASE}/billing/process-complaint-charge/{ticket_id}", 
                                              headers=headers)
                
                if charge_response.status_code == 200:
                    data = charge_response.json()
                    self.log(f"Complaint charge processed: {data.get('message')}")
                    return True
                else:
                    self.log(f"Complaint charge processing failed: {charge_response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"Test ticket creation failed: {ticket_response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Complaint charge processing error: {e}", "ERROR")
            return False
    
    def test_stripe_webhook_simulation(self) -> bool:
        """Test Stripe webhook handling"""
        try:
            self.log("Testing Stripe webhook simulation...")
            headers = {"Content-Type": "application/json"}
            
            # Simulate a payment_intent.succeeded webhook
            webhook_data = {
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": "pi_test_webhook",
                        "status": "succeeded",
                        "amount": 10000,
                        "currency": "inr",
                        "metadata": {
                            "brand_id": str(self.test_brand_id),
                            "type": "credit_topup"
                        }
                    }
                }
            }
            
            response = requests.post(f"{API_BASE}/billing/webhook/stripe", 
                                   json=webhook_data, headers=headers)
            
            if response.status_code == 200:
                self.log("Stripe webhook processed successfully")
                return True
            else:
                self.log(f"Stripe webhook failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Stripe webhook error: {e}", "ERROR")
            return False
    
    def test_billing_export(self) -> bool:
        """Test billing data export"""
        try:
            self.log("Testing billing data export...")
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_BASE}/billing/admin/export?format=csv&date_range=30d", 
                                  headers=headers)
            
            if response.status_code == 200:
                self.log("Billing data export successful")
                return True
            else:
                self.log(f"Billing data export failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Billing data export error: {e}", "ERROR")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all billing system tests"""
        self.log("Starting Advanced Billing & Payment Integration Tests")
        self.log("=" * 60)
        
        results = {}
        
        # Authentication tests
        results["admin_login"] = self.login_admin()
        results["brand_login"] = self.login_brand()
        
        if not results["admin_login"] or not results["brand_login"]:
            self.log("Authentication failed. Please check credentials.", "ERROR")
            return results
        
        # Brand user tests
        results["billing_summary"] = self.test_billing_summary()
        results["transaction_history"] = self.test_transaction_history()
        results["subscription_plans"] = self.test_subscription_plans()
        results["billing_analytics"] = self.test_billing_analytics()
        results["credit_topup_creation"] = self.test_credit_topup_creation()
        results["invoice_generation"] = self.test_invoice_generation()
        
        # Admin tests
        results["admin_billing_logs"] = self.test_admin_billing_logs()
        results["refund_processing"] = self.test_refund_processing()
        results["complaint_charge_processing"] = self.test_complaint_charge_processing()
        results["billing_export"] = self.test_billing_export()
        
        # Webhook tests
        results["stripe_webhook"] = self.test_stripe_webhook_simulation()
        
        # Summary
        self.log("=" * 60)
        self.log("Test Results Summary:")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.log(f"  {test_name}: {status}")
        
        self.log(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All billing system tests passed!", "SUCCESS")
        else:
            self.log(f"❌ {total - passed} tests failed", "ERROR")
        
        return results

def main():
    """Main function"""
    print("Advanced Billing & Payment Integration Test Script")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running. Please start the server first.")
        sys.exit(1)
    
    print("✅ Backend server is running")
    
    # Run tests
    tester = BillingSystemTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 