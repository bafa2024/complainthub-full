#!/usr/bin/env python3
"""
Advanced Analytics & Reporting System Test Script
Tests comprehensive analytics features including real-time metrics, reporting, and predictive analytics
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (you may need to adjust these)
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

BRAND_CREDENTIALS = {
    "email": "brand@example.com", 
    "password": "brand123"
}

USER_CREDENTIALS = {
    "email": "user@example.com",
    "password": "user123"
}

class AnalyticsTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.brand_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate(self):
        """Authenticate with different user types"""
        print("\n🔐 Authenticating users...")
        
        # Admin authentication
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                self.admin_token = response.json().get("access_token")
                self.log_test("Admin Authentication", True, "Admin token obtained")
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Authentication", False, str(e))
        
        # Brand authentication
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=BRAND_CREDENTIALS)
            if response.status_code == 200:
                self.brand_token = response.json().get("access_token")
                self.log_test("Brand Authentication", True, "Brand token obtained")
            else:
                self.log_test("Brand Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Brand Authentication", False, str(e))
        
        # User authentication
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                self.user_token = response.json().get("access_token")
                self.log_test("User Authentication", True, "User token obtained")
            else:
                self.log_test("User Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User Authentication", False, str(e))
    
    def test_system_overview(self):
        """Test system overview analytics"""
        print("\n📊 Testing System Overview Analytics...")
        
        if not self.admin_token:
            self.log_test("System Overview", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different date ranges
        date_ranges = ["7d", "30d", "90d", "1y"]
        
        for date_range in date_ranges:
            try:
                response = self.session.get(
                    f"{API_BASE}/analytics/overview?date_range={date_range}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    overview = data.get("data", {}).get("overview", {})
                    
                    # Validate required fields
                    required_fields = [
                        "total_users", "total_brands", "total_tickets", 
                        "resolution_rate", "avg_resolution_time", "avg_satisfaction"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in overview]
                    
                    if not missing_fields:
                        self.log_test(
                            f"System Overview ({date_range})", 
                            True, 
                            f"Retrieved overview with {overview.get('total_tickets', 0)} tickets"
                        )
                    else:
                        self.log_test(
                            f"System Overview ({date_range})", 
                            False, 
                            f"Missing fields: {missing_fields}"
                        )
                else:
                    self.log_test(
                        f"System Overview ({date_range})", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"System Overview ({date_range})", False, str(e))
    
    def test_brand_analytics(self):
        """Test brand-specific analytics"""
        print("\n🏢 Testing Brand Analytics...")
        
        if not self.brand_token:
            self.log_test("Brand Analytics", False, "No brand token available")
            return
        
        headers = {"Authorization": f"Bearer {self.brand_token}"}
        
        # Test brand analytics (brand_id = 1 for testing)
        try:
            response = self.session.get(
                f"{API_BASE}/analytics/brand/1?date_range=30d",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                brand_data = data.get("data", {})
                
                # Validate required fields
                required_fields = [
                    "brand_id", "total_tickets", "resolved_tickets", 
                    "resolution_rate", "avg_response_time", "avg_resolution_time"
                ]
                
                missing_fields = [field for field in required_fields if field not in brand_data]
                
                if not missing_fields:
                    self.log_test(
                        "Brand Analytics", 
                        True, 
                        f"Retrieved analytics for brand {brand_data.get('brand_id')}"
                    )
                else:
                    self.log_test("Brand Analytics", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Brand Analytics", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Brand Analytics", False, str(e))
    
    def test_user_analytics(self):
        """Test user-specific analytics"""
        print("\n👤 Testing User Analytics...")
        
        if not self.user_token:
            self.log_test("User Analytics", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test user analytics (user_id = 1 for testing)
        try:
            response = self.session.get(
                f"{API_BASE}/analytics/user/1?date_range=30d",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("data", {})
                
                # Validate required fields
                required_fields = [
                    "user_id", "total_complaints", "resolved_complaints", 
                    "resolution_rate", "avg_satisfaction"
                ]
                
                missing_fields = [field for field in required_fields if field not in user_data]
                
                if not missing_fields:
                    self.log_test(
                        "User Analytics", 
                        True, 
                        f"Retrieved analytics for user {user_data.get('user_id')}"
                    )
                else:
                    self.log_test("User Analytics", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("User Analytics", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("User Analytics", False, str(e))
    
    def test_real_time_metrics(self):
        """Test real-time metrics"""
        print("\n⚡ Testing Real-time Metrics...")
        
        if not self.admin_token:
            self.log_test("Real-time Metrics", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(f"{API_BASE}/analytics/realtime", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                realtime_data = data.get("data", {})
                
                # Validate required fields
                required_fields = [
                    "today_tickets", "last_hour_tickets", "active_conversations", 
                    "pending_tickets", "recent_activity", "system_health"
                ]
                
                missing_fields = [field for field in required_fields if field not in realtime_data]
                
                if not missing_fields:
                    self.log_test(
                        "Real-time Metrics", 
                        True, 
                        f"Retrieved real-time data with {realtime_data.get('today_tickets', 0)} today tickets"
                    )
                else:
                    self.log_test("Real-time Metrics", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Real-time Metrics", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Real-time Metrics", False, str(e))
    
    def test_report_generation(self):
        """Test report generation"""
        print("\n📋 Testing Report Generation...")
        
        if not self.admin_token:
            self.log_test("Report Generation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different report types
        report_types = ["performance", "trends", "financial", "customer_satisfaction", "channel_analysis"]
        
        for report_type in report_types:
            try:
                response = self.session.post(
                    f"{API_BASE}/analytics/reports/{report_type}",
                    headers=headers,
                    json={"date_range": "30d"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    report_data = data.get("data", {})
                    
                    if report_data.get("report_type") == report_type:
                        self.log_test(
                            f"Report Generation ({report_type})", 
                            True, 
                            f"Generated {report_type} report"
                        )
                    else:
                        self.log_test(
                            f"Report Generation ({report_type})", 
                            False, 
                            "Invalid report type in response"
                        )
                else:
                    self.log_test(
                        f"Report Generation ({report_type})", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Report Generation ({report_type})", False, str(e))
    
    def test_predictive_analytics(self):
        """Test predictive analytics"""
        print("\n🔮 Testing Predictive Analytics...")
        
        if not self.admin_token:
            self.log_test("Predictive Analytics", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different metrics
        metrics = ["ticket_volume", "resolution_time", "satisfaction"]
        
        for metric in metrics:
            try:
                response = self.session.get(
                    f"{API_BASE}/analytics/predictive/{metric}?days=30",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    prediction_data = data.get("data", {})
                    
                    if "predictions" in prediction_data:
                        self.log_test(
                            f"Predictive Analytics ({metric})", 
                            True, 
                            f"Generated predictions for {metric}"
                        )
                    else:
                        self.log_test(
                            f"Predictive Analytics ({metric})", 
                            False, 
                            "No predictions in response"
                        )
                else:
                    self.log_test(
                        f"Predictive Analytics ({metric})", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Predictive Analytics ({metric})", False, str(e))
    
    def test_trends_analysis(self):
        """Test trends analysis"""
        print("\n📈 Testing Trends Analysis...")
        
        if not self.admin_token:
            self.log_test("Trends Analysis", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different metrics
        metrics = ["tickets", "satisfaction", "resolution_time"]
        
        for metric in metrics:
            try:
                response = self.session.get(
                    f"{API_BASE}/analytics/trends?date_range=30d&metric={metric}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    trends_data = data.get("data", {})
                    
                    if "daily_tickets" in trends_data or "growth_rate" in trends_data:
                        self.log_test(
                            f"Trends Analysis ({metric})", 
                            True, 
                            f"Retrieved trends for {metric}"
                        )
                    else:
                        self.log_test(
                            f"Trends Analysis ({metric})", 
                            False, 
                            "No trends data in response"
                        )
                else:
                    self.log_test(
                        f"Trends Analysis ({metric})", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Trends Analysis ({metric})", False, str(e))
    
    def test_metric_comparison(self):
        """Test metric comparison"""
        print("\n⚖️ Testing Metric Comparison...")
        
        if not self.admin_token:
            self.log_test("Metric Comparison", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(
                f"{API_BASE}/analytics/comparison?metric=resolution_rate&period1=7d&period2=30d",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                comparison_data = data.get("data", {})
                
                if "comparison" in comparison_data:
                    comparison = comparison_data["comparison"]
                    if "change_percent" in comparison:
                        self.log_test(
                            "Metric Comparison", 
                            True, 
                            f"Compared metrics with {comparison['change_percent']}% change"
                        )
                    else:
                        self.log_test("Metric Comparison", False, "No change percentage in comparison")
                else:
                    self.log_test("Metric Comparison", False, "No comparison data in response")
            else:
                self.log_test("Metric Comparison", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Metric Comparison", False, str(e))
    
    def test_report_export(self):
        """Test report export"""
        print("\n📤 Testing Report Export...")
        
        if not self.admin_token:
            self.log_test("Report Export", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different export formats
        formats = ["json", "csv"]
        
        for export_format in formats:
            try:
                response = self.session.get(
                    f"{API_BASE}/analytics/export/performance?format={export_format}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if export_format == "json" and "data" in data:
                        self.log_test(
                            f"Report Export ({export_format})", 
                            True, 
                            f"Exported {export_format} report"
                        )
                    elif export_format == "csv" and "data" in data:
                        self.log_test(
                            f"Report Export ({export_format})", 
                            True, 
                            f"Exported {export_format} report"
                        )
                    else:
                        self.log_test(
                            f"Report Export ({export_format})", 
                            False, 
                            "Invalid export data"
                        )
                else:
                    self.log_test(
                        f"Report Export ({export_format})", 
                        False, 
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Report Export ({export_format})", False, str(e))
    
    def test_dashboard_data(self):
        """Test dashboard data retrieval"""
        print("\n📊 Testing Dashboard Data...")
        
        if not self.admin_token:
            self.log_test("Dashboard Data", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(
                f"{API_BASE}/analytics/dashboard?date_range=30d",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                dashboard_data = data.get("data", {})
                
                # Validate required sections
                required_sections = ["overview", "real_time", "user_role", "date_range"]
                
                missing_sections = [section for section in required_sections if section not in dashboard_data]
                
                if not missing_sections:
                    self.log_test(
                        "Dashboard Data", 
                        True, 
                        f"Retrieved dashboard data for {dashboard_data.get('user_role')} user"
                    )
                else:
                    self.log_test("Dashboard Data", False, f"Missing sections: {missing_sections}")
            else:
                self.log_test("Dashboard Data", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Dashboard Data", False, str(e))
    
    def test_analytics_health(self):
        """Test analytics system health"""
        print("\n🏥 Testing Analytics Health...")
        
        if not self.admin_token:
            self.log_test("Analytics Health", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(f"{API_BASE}/analytics/health", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                health_data = data.get("data", {})
                
                if "status" in health_data:
                    self.log_test(
                        "Analytics Health", 
                        True, 
                        f"System status: {health_data['status']}"
                    )
                else:
                    self.log_test("Analytics Health", False, "No status in health data")
            else:
                self.log_test("Analytics Health", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Health", False, str(e))
    
    def test_access_control(self):
        """Test access control for analytics endpoints"""
        print("\n🔒 Testing Access Control...")
        
        # Test admin-only endpoints with brand token
        if self.brand_token:
            headers = {"Authorization": f"Bearer {self.brand_token}"}
            
            try:
                response = self.session.get(f"{API_BASE}/analytics/overview", headers=headers)
                
                if response.status_code == 403:
                    self.log_test("Access Control (Brand to Admin)", True, "Properly denied access")
                else:
                    self.log_test("Access Control (Brand to Admin)", False, f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Access Control (Brand to Admin)", False, str(e))
        
        # Test brand analytics with user token
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            try:
                response = self.session.get(f"{API_BASE}/analytics/brand/1", headers=headers)
                
                if response.status_code == 403:
                    self.log_test("Access Control (User to Brand)", True, "Properly denied access")
                else:
                    self.log_test("Access Control (User to Brand)", False, f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Access Control (User to Brand)", False, str(e))
    
    def run_all_tests(self):
        """Run all analytics tests"""
        print("🚀 Starting Advanced Analytics & Reporting System Tests")
        print("=" * 60)
        
        # Authenticate first
        self.authenticate()
        
        # Run all test suites
        self.test_system_overview()
        self.test_brand_analytics()
        self.test_user_analytics()
        self.test_real_time_metrics()
        self.test_report_generation()
        self.test_predictive_analytics()
        self.test_trends_analysis()
        self.test_metric_comparison()
        self.test_report_export()
        self.test_dashboard_data()
        self.test_analytics_health()
        self.test_access_control()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ANALYTICS SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "test_run": timestamp,
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")
        
        if failed_tests == 0:
            print("\n🎉 All analytics tests passed! The system is working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please review the failed tests above.")

def main():
    """Main function"""
    print("Advanced Analytics & Reporting System Test Suite")
    print("This script tests comprehensive analytics features including:")
    print("- System overview analytics")
    print("- Brand and user-specific analytics") 
    print("- Real-time metrics")
    print("- Report generation")
    print("- Predictive analytics")
    print("- Trends analysis")
    print("- Metric comparison")
    print("- Report export")
    print("- Dashboard data")
    print("- System health monitoring")
    print("- Access control")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print(f"\n❌ Server not responding properly at {BASE_URL}")
            print("Please ensure the FastAPI server is running with: uvicorn app.main:app --reload")
            return
    except requests.exceptions.RequestException:
        print(f"\n❌ Cannot connect to server at {BASE_URL}")
        print("Please ensure the FastAPI server is running with: uvicorn app.main:app --reload")
        return
    
    print(f"\n✅ Server is running at {BASE_URL}")
    
    # Run tests
    tester = AnalyticsTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 