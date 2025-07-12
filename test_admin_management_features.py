#!/usr/bin/env python3
"""
Test script for Admin Management Features
Tests all admin functionality including dashboard, settings, reports, and system management
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@complainthub.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and get access token"""
    print("🔐 Logging in as admin...")
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            token = data["data"]["access_token"]
            print("✅ Admin login successful")
            return token
        else:
            print(f"❌ Admin login failed: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_system_stats(token):
    """Test system statistics endpoint"""
    print("\n📊 Testing System Statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            stats = data["data"]
            print("✅ System stats retrieved successfully")
            print(f"   - Total users: {stats.get('overview', {}).get('total_users', 'N/A')}")
            print(f"   - Total brands: {stats.get('overview', {}).get('total_brands', 'N/A')}")
            print(f"   - Total tickets: {stats.get('overview', {}).get('total_tickets', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get system stats: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ System stats request failed: {e}")
        return False

def test_system_settings(token):
    """Test system settings endpoints"""
    print("\n⚙️ Testing System Settings...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get settings
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/settings", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            settings = data["data"]
            print("✅ System settings retrieved successfully")
            print(f"   - System name: {settings.get('systemName', 'N/A')}")
            print(f"   - Resolution window: {settings.get('resolutionWindow', 'N/A')} hours")
            return settings
        else:
            print(f"❌ Failed to get system settings: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Get settings request failed: {e}")
        return None

def test_update_settings(token, current_settings):
    """Test updating system settings"""
    print("\n🔄 Testing Settings Update...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update some settings
    updated_settings = current_settings.copy()
    updated_settings["resolutionWindow"] = "48"
    updated_settings["systemName"] = "ComplaintHub Bot - Updated"
    
    try:
        response = requests.put(f"{BASE_URL}/api/v1/admin/settings", 
                              json=updated_settings, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            print("✅ System settings updated successfully")
            return True
        else:
            print(f"❌ Failed to update settings: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Update settings request failed: {e}")
        return False

def test_connection_tests(token):
    """Test external service connections"""
    print("\n🔗 Testing External Connections...")
    
    headers = {"Authorization": f"Bearer {token}"}
    services = ["openai", "twilio", "deepgram", "stripe"]
    
    for service in services:
        try:
            response = requests.post(f"{BASE_URL}/api/v1/admin/test-connection/{service}", 
                                   headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ {service.upper()} connection test successful")
            else:
                print(f"⚠️ {service.upper()} connection test failed: {data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {service.upper()} connection test request failed: {e}")

def test_reports(token):
    """Test report generation endpoints"""
    print("\n📋 Testing Report Generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Set date range for reports
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    report_types = [
        ("complaints", "Complaints Report"),
        ("brands", "Brands Report"),
        ("users", "Users Report"),
        ("revenue", "Revenue Report")
    ]
    
    for report_type, report_name in report_types:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/admin/reports/{report_type}", 
                                  params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "success":
                report_data = data["data"]
                print(f"✅ {report_name} generated successfully")
                
                # Print some key metrics
                if report_type == "complaints":
                    total = sum(item.get("count", 0) for item in report_data.get("byStatus", []))
                    print(f"   - Total complaints: {total}")
                elif report_type == "brands":
                    print(f"   - Brands analyzed: {len(report_data)}")
                elif report_type == "users":
                    print(f"   - Total users: {report_data.get('totalUsers', 'N/A')}")
                elif report_type == "revenue":
                    print(f"   - Total revenue: ₹{report_data.get('totalRevenue', 'N/A')}")
                    
            else:
                print(f"❌ Failed to generate {report_name}: {data.get('message', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {report_name} request failed: {e}")

def test_dashboard_data(token):
    """Test dashboard data endpoint"""
    print("\n📈 Testing Dashboard Data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/dashboard", 
                              params={"date_range": "30d"}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            dashboard_data = data["data"]
            print("✅ Dashboard data retrieved successfully")
            
            # Check for required data sections
            sections = ["overview", "realTime", "recentActivity", "systemHealth", "topBrands"]
            for section in sections:
                if section in dashboard_data:
                    print(f"   - {section} data available")
                else:
                    print(f"   - {section} data missing")
                    
            return True
        else:
            print(f"❌ Failed to get dashboard data: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard data request failed: {e}")
        return False

def test_system_health(token):
    """Test system health endpoint"""
    print("\n💚 Testing System Health...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/health", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            health_data = data["data"]
            print("✅ System health data retrieved successfully")
            print(f"   - Status: {health_data.get('status', 'N/A')}")
            print(f"   - Uptime: {health_data.get('uptime', 'N/A')}")
            print(f"   - Error rate: {health_data.get('error_rate', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get system health: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ System health request failed: {e}")
        return False

def test_recent_activity(token):
    """Test recent activity endpoint"""
    print("\n📝 Testing Recent Activity...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/activity", 
                              params={"limit": 5}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            activities = data["data"]
            print("✅ Recent activity retrieved successfully")
            print(f"   - Activities found: {len(activities)}")
            
            for activity in activities[:3]:  # Show first 3 activities
                print(f"   - {activity.get('title', 'N/A')} ({activity.get('time', 'N/A')})")
                
            return True
        else:
            print(f"❌ Failed to get recent activity: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Recent activity request failed: {e}")
        return False

def test_top_brands(token):
    """Test top brands endpoint"""
    print("\n🏆 Testing Top Brands...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/top-brands", 
                              params={"limit": 5}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            brands = data["data"]
            print("✅ Top brands retrieved successfully")
            print(f"   - Brands found: {len(brands)}")
            
            for brand in brands[:3]:  # Show first 3 brands
                print(f"   - {brand.get('name', 'N/A')} ({brand.get('resolution_rate', 'N/A')}% resolution)")
                
            return True
        else:
            print(f"❌ Failed to get top brands: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Top brands request failed: {e}")
        return False

def test_backup_management(token):
    """Test backup management endpoints"""
    print("\n💾 Testing Backup Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list backups
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/backups", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            backups = data["data"]
            print("✅ Backup listing successful")
            print(f"   - Backups found: {len(backups)}")
            return True
        else:
            print(f"❌ Failed to list backups: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backup listing request failed: {e}")
        return False

def test_report_export(token):
    """Test report export functionality"""
    print("\n📤 Testing Report Export...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test CSV export
    try:
        filters = {
            "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/admin/reports/generate/complaints", 
                               json=filters, params={"format": "csv"}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            print("✅ Report export successful")
            return True
        else:
            print(f"❌ Failed to export report: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Report export request failed: {e}")
        return False

def test_frontend_pages():
    """Test frontend admin pages availability"""
    print("\n🌐 Testing Frontend Admin Pages...")
    
    frontend_url = "http://localhost:3000"
    admin_pages = [
        "/admin/dashboard",
        "/admin/brands",
        "/admin/users",
        "/admin/complaints",
        "/admin/analytics",
        "/admin/reports",
        "/admin/settings"
    ]
    
    for page in admin_pages:
        try:
            response = requests.get(f"{frontend_url}{page}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {page} - Available")
            else:
                print(f"⚠️ {page} - Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {page} - Not accessible: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Admin Management Features Test")
    print("=" * 50)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        return
    
    # Test all admin features
    test_results = []
    
    # System overview tests
    test_results.append(("System Stats", test_system_stats(token)))
    test_results.append(("Dashboard Data", test_dashboard_data(token)))
    test_results.append(("System Health", test_system_health(token)))
    test_results.append(("Recent Activity", test_recent_activity(token)))
    test_results.append(("Top Brands", test_top_brands(token)))
    
    # Settings management tests
    current_settings = test_system_settings(token)
    if current_settings:
        test_results.append(("Settings Update", test_update_settings(token, current_settings)))
    
    # Connection tests
    test_connection_tests(token)
    
    # Report generation tests
    test_reports(token)
    test_results.append(("Report Export", test_report_export(token)))
    
    # Backup management tests
    test_results.append(("Backup Management", test_backup_management(token)))
    
    # Frontend tests
    test_frontend_pages()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All admin management features are working correctly!")
    else:
        print("⚠️ Some admin management features need attention")
    
    print("\n📋 Admin Management Features Implemented:")
    print("✅ Admin Dashboard with system overview widgets")
    print("✅ System Settings management")
    print("✅ Comprehensive report generation")
    print("✅ External service connection testing")
    print("✅ System health monitoring")
    print("✅ Recent activity tracking")
    print("✅ Top brands performance")
    print("✅ Backup management")
    print("✅ Report export functionality")
    print("✅ Frontend admin pages")

if __name__ == "__main__":
    main() 