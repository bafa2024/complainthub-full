# backend/app/services/admin.py

import logging
import json
import os
import subprocess
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.models import User, Brand, Ticket, SystemSettings, Conversation
from app.core.config import settings

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_settings(self) -> Dict[str, Any]:
        """
        Get system settings from database or return defaults
        """
        try:
            # Get settings from database
            settings_record = self.db.query(SystemSettings).first()
            
            if settings_record:
                return json.loads(settings_record.settings_data)
            else:
                # Return default settings
                return self._get_default_settings()
                
        except Exception as e:
            logger.error(f"Error getting system settings: {e}")
            return self._get_default_settings()
    
    def update_system_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update system settings in database
        """
        try:
            settings_record = self.db.query(SystemSettings).first()
            
            if settings_record:
                settings_record.settings_data = json.dumps(settings_data)
                settings_record.updated_at = datetime.utcnow()
            else:
                settings_record = SystemSettings(
                    settings_data=json.dumps(settings_data),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(settings_record)
            
            self.db.commit()
            
            return settings_data
            
        except Exception as e:
            logger.error(f"Error updating system settings: {e}")
            self.db.rollback()
            raise
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default system settings
        """
        return {
            # API Credentials
            "openAiKey": "",
            "twilioSid": "",
            "twilioToken": "",
            "deepgramKey": "",
            "stripeSecretKey": "",
            "stripePublishableKey": "",
            
            # Business Rules
            "feeAmount": "50",
            "resolutionWindow": "24",
            "maxTicketsPerUser": "10",
            "autoCloseDays": "7",
            "satisfactionThreshold": "3.5",
            
            # System Configuration
            "systemName": "ComplaintHub Bot",
            "systemEmail": "admin@complainthub.com",
            "timezone": "Asia/Kolkata",
            "maintenanceMode": False,
            "debugMode": False,
            
            # Security Settings
            "sessionTimeout": "8",
            "maxLoginAttempts": "5",
            "passwordMinLength": "8",
            "requireTwoFactor": False,
            "allowedDomains": "",
            
            # Notification Settings
            "emailNotifications": True,
            "smsNotifications": True,
            "pushNotifications": True,
            "notificationFrequency": "immediate",
            
            # Integration Settings
            "enableWhatsApp": True,
            "enableTelegram": True,
            "enableVoice": True,
            "enableEmail": True,
            
            # Analytics Settings
            "enableAnalytics": True,
            "dataRetentionDays": "365",
            "enableTracking": True,
            
            # Backup Settings
            "autoBackup": True,
            "backupFrequency": "daily",
            "backupRetention": "30"
        }
    
    def test_connection(self, service: str) -> Dict[str, Any]:
        """
        Test external service connection
        """
        try:
            if service == "openai":
                return self._test_openai_connection()
            elif service == "twilio":
                return self._test_twilio_connection()
            elif service == "deepgram":
                return self._test_deepgram_connection()
            elif service == "stripe":
                return self._test_stripe_connection()
            else:
                return {"success": False, "error": f"Unknown service: {service}"}
                
        except Exception as e:
            logger.error(f"Error testing {service} connection: {e}")
            return {"success": False, "error": str(e)}
    
    def _test_openai_connection(self) -> Dict[str, Any]:
        """
        Test OpenAI API connection
        """
        try:
            settings = self.get_system_settings()
            api_key = settings.get("openAiKey")
            
            if not api_key:
                return {"success": False, "error": "OpenAI API key not configured"}
            
            # Test with a simple request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "OpenAI connection successful"}
            else:
                return {"success": False, "error": f"OpenAI API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_twilio_connection(self) -> Dict[str, Any]:
        """
        Test Twilio API connection
        """
        try:
            settings = self.get_system_settings()
            account_sid = settings.get("twilioSid")
            auth_token = settings.get("twilioToken")
            
            if not account_sid or not auth_token:
                return {"success": False, "error": "Twilio credentials not configured"}
            
            # Test with account info request
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
            response = requests.get(url, auth=(account_sid, auth_token), timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "Twilio connection successful"}
            else:
                return {"success": False, "error": f"Twilio API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_deepgram_connection(self) -> Dict[str, Any]:
        """
        Test Deepgram API connection
        """
        try:
            settings = self.get_system_settings()
            api_key = settings.get("deepgramKey")
            
            if not api_key:
                return {"success": False, "error": "Deepgram API key not configured"}
            
            # Test with account info request
            headers = {"Authorization": f"Token {api_key}"}
            response = requests.get("https://api.deepgram.com/v1/projects", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "Deepgram connection successful"}
            else:
                return {"success": False, "error": f"Deepgram API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_stripe_connection(self) -> Dict[str, Any]:
        """
        Test Stripe API connection
        """
        try:
            settings = self.get_system_settings()
            secret_key = settings.get("stripeSecretKey")
            
            if not secret_key:
                return {"success": False, "error": "Stripe secret key not configured"}
            
            # Test with account info request
            headers = {"Authorization": f"Bearer {secret_key}"}
            response = requests.get("https://api.stripe.com/v1/account", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "Stripe connection successful"}
            else:
                return {"success": False, "error": f"Stripe API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_system(self) -> Dict[str, Any]:
        """
        Restart system services
        """
        try:
            # This is a placeholder - in production, you'd implement actual service restart
            logger.info("System restart requested by admin")
            
            # For now, just return success
            return {
                "success": True,
                "message": "System restart initiated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error restarting system: {e}")
            raise
    
    def get_complaints_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate complaints report
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            
            # Get complaints in date range
            tickets = self.db.query(Ticket).filter(
                Ticket.created_at >= start,
                Ticket.created_at < end
            ).all()
            
            # Calculate statistics
            total_complaints = len(tickets)
            resolved = len([t for t in tickets if t.status == "resolved"])
            in_progress = len([t for t in tickets if t.status == "in-progress"])
            pending = len([t for t in tickets if t.status == "new"])
            
            # Status breakdown
            by_status = [
                {"status": "Resolved", "count": resolved, "percentage": round((resolved/total_complaints)*100, 1) if total_complaints > 0 else 0},
                {"status": "In Progress", "count": in_progress, "percentage": round((in_progress/total_complaints)*100, 1) if total_complaints > 0 else 0},
                {"status": "Pending", "count": pending, "percentage": round((pending/total_complaints)*100, 1) if total_complaints > 0 else 0}
            ]
            
            # Category breakdown
            categories = {}
            for ticket in tickets:
                category = ticket.category or "Other"
                categories[category] = categories.get(category, 0) + 1
            
            by_category = [
                {"category": cat, "count": count, "percentage": round((count/total_complaints)*100, 1) if total_complaints > 0 else 0}
                for cat, count in categories.items()
            ]
            
            # Brand breakdown
            brand_stats = {}
            for ticket in tickets:
                if ticket.brand_id:
                    brand_name = ticket.brand.name if ticket.brand else "Unknown"
                    if brand_name not in brand_stats:
                        brand_stats[brand_name] = {"count": 0, "resolved": 0, "total_time": 0}
                    brand_stats[brand_name]["count"] += 1
                    if ticket.status == "resolved":
                        brand_stats[brand_name]["resolved"] += 1
                    if ticket.resolved_at and ticket.created_at:
                        resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                        brand_stats[brand_name]["total_time"] += resolution_time
            
            by_brand = []
            for brand_name, stats in brand_stats.items():
                avg_resolution = round(stats["total_time"] / stats["resolved"], 1) if stats["resolved"] > 0 else 0
                resolution_rate = round((stats["resolved"] / stats["count"]) * 100, 1)
                by_brand.append({
                    "brand": brand_name,
                    "count": stats["count"],
                    "avgResolution": f"{avg_resolution}h",
                    "resolutionRate": resolution_rate,
                    "satisfactionScore": 4.2  # Placeholder
                })
            
            return {
                "byStatus": by_status,
                "byCategory": by_category,
                "byBrand": sorted(by_brand, key=lambda x: x["count"], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error generating complaints report: {e}")
            raise
    
    def get_brands_report(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Generate brands report
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            
            # Get all brands with their statistics
            brands = self.db.query(Brand).all()
            brand_reports = []
            
            for brand in brands:
                # Get brand tickets in date range
                tickets = self.db.query(Ticket).filter(
                    Ticket.brand_id == brand.id,
                    Ticket.created_at >= start,
                    Ticket.created_at < end
                ).all()
                
                total_complaints = len(tickets)
                resolved = len([t for t in tickets if t.status == "resolved"])
                resolution_rate = round((resolved / total_complaints) * 100, 1) if total_complaints > 0 else 0
                
                # Calculate average response time
                total_time = 0
                resolved_count = 0
                for ticket in tickets:
                    if ticket.resolved_at and ticket.created_at:
                        resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                        total_time += resolution_time
                        resolved_count += 1
                
                avg_response_time = round(total_time / resolved_count, 1) if resolved_count > 0 else 0
                
                brand_reports.append({
                    "name": brand.name,
                    "industry": brand.industry,
                    "totalComplaints": total_complaints,
                    "resolved": resolved,
                    "resolutionRate": resolution_rate,
                    "avgResponseTime": avg_response_time,
                    "satisfactionScore": 4.2,  # Placeholder
                    "revenue": 5000  # Placeholder
                })
            
            return sorted(brand_reports, key=lambda x: x["totalComplaints"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating brands report: {e}")
            raise
    
    def get_users_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate users report
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            
            # Get user statistics
            total_users = self.db.query(User).count()
            new_users = self.db.query(User).filter(
                User.created_at >= start,
                User.created_at < end
            ).count()
            
            # Get active users (users with tickets in date range)
            active_users = self.db.query(User).join(Ticket).filter(
                Ticket.created_at >= start,
                Ticket.created_at < end
            ).distinct().count()
            
            # Calculate average complaints per user
            total_tickets = self.db.query(Ticket).filter(
                Ticket.created_at >= start,
                Ticket.created_at < end
            ).count()
            
            avg_complaints_per_user = round(total_tickets / total_users, 1) if total_users > 0 else 0
            
            return {
                "totalUsers": total_users,
                "newUsers": new_users,
                "activeUsers": active_users,
                "avgComplaintsPerUser": avg_complaints_per_user,
                "mostActiveUsers": 150,  # Placeholder
                "userSatisfaction": 4.2  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error generating users report: {e}")
            raise
    
    def get_revenue_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate revenue report
        """
        try:
            # This is a placeholder - implement actual revenue calculation
            return {
                "totalRevenue": 45600,
                "monthlyRevenue": 45600,
                "growthRate": 15,
                "topBrands": [
                    {"name": "TechCorp Solutions", "revenue": 8500},
                    {"name": "Global Retail", "revenue": 7200},
                    {"name": "Digital Services", "revenue": 6800},
                    {"name": "Mobile Telecom", "revenue": 5500},
                    {"name": "Cloud Computing", "revenue": 4800}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue report: {e}")
            raise
    
    def generate_report(self, report_type: str, format: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and export report
        """
        try:
            if report_type == "complaints":
                data = self.get_complaints_report(filters.get("startDate"), filters.get("endDate"))
            elif report_type == "brands":
                data = self.get_brands_report(filters.get("startDate"), filters.get("endDate"))
            elif report_type == "users":
                data = self.get_users_report(filters.get("startDate"), filters.get("endDate"))
            elif report_type == "revenue":
                data = self.get_revenue_report(filters.get("startDate"), filters.get("endDate"))
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            if format == "json":
                return {"success": True, "data": json.dumps(data, indent=2)}
            elif format == "csv":
                return {"success": True, "data": self._convert_to_csv(data)}
            elif format == "pdf":
                return {"success": True, "data": self._convert_to_pdf(data, report_type)}
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """
        Convert data to CSV format
        """
        # This is a simplified CSV conversion
        csv_lines = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        # List of dictionaries
                        headers = list(value[0].keys())
                        csv_lines.append(",".join(headers))
                        for item in value:
                            row = [str(item.get(header, "")) for header in headers]
                            csv_lines.append(",".join(row))
                    else:
                        # Simple list
                        csv_lines.append(f"{key},{','.join(map(str, value))}")
                else:
                    csv_lines.append(f"{key},{value}")
        
        return "\n".join(csv_lines)
    
    def _convert_to_pdf(self, data: Dict[str, Any], report_type: str) -> str:
        """
        Convert data to PDF format (placeholder)
        """
        # This is a placeholder - implement actual PDF generation
        return f"PDF report for {report_type} would be generated here"
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health status
        """
        try:
            # This is a placeholder - implement actual health checks
            return {
                "status": "healthy",
                "uptime": "99.9%",
                "error_rate": 0.001,
                "avg_response_time": 150,
                "database_status": "connected",
                "api_status": "operational",
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent system activity
        """
        try:
            # This is a placeholder - implement actual activity tracking
            activities = [
                {
                    "type": "ticket_created",
                    "title": "New complaint submitted",
                    "time": "2 minutes ago",
                    "icon": "fa-ticket-alt"
                },
                {
                    "type": "user_registered",
                    "title": "New user registered",
                    "time": "5 minutes ago",
                    "icon": "fa-user-plus"
                },
                {
                    "type": "ticket_resolved",
                    "title": "Complaint resolved",
                    "time": "10 minutes ago",
                    "icon": "fa-check-circle"
                },
                {
                    "type": "brand_created",
                    "title": "New brand added",
                    "time": "1 hour ago",
                    "icon": "fa-building"
                },
                {
                    "type": "system_backup",
                    "title": "System backup completed",
                    "time": "2 hours ago",
                    "icon": "fa-database"
                }
            ]
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            raise
    
    def get_top_brands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing brands
        """
        try:
            # Get brands with their performance metrics
            brands = self.db.query(Brand).all()
            brand_performance = []
            
            for brand in brands:
                tickets = self.db.query(Ticket).filter(Ticket.brand_id == brand.id).all()
                total_tickets = len(tickets)
                resolved_tickets = len([t for t in tickets if t.status == "resolved"])
                resolution_rate = round((resolved_tickets / total_tickets) * 100, 1) if total_tickets > 0 else 0
                
                brand_performance.append({
                    "name": brand.name,
                    "resolution_rate": resolution_rate,
                    "avg_response_time": 2.3,  # Placeholder
                    "total_tickets": total_tickets
                })
            
            # Sort by resolution rate and return top brands
            sorted_brands = sorted(brand_performance, key=lambda x: x["resolution_rate"], reverse=True)
            return sorted_brands[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top brands: {e}")
            raise
    
    def create_backup(self) -> Dict[str, Any]:
        """
        Create system backup
        """
        try:
            # This is a placeholder - implement actual backup logic
            backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "backup_id": backup_id,
                "created_at": datetime.utcnow().isoformat(),
                "size": "150MB",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups
        """
        try:
            # This is a placeholder - implement actual backup listing
            return [
                {
                    "backup_id": "backup_20240115_143022",
                    "created_at": "2024-01-15T14:30:22",
                    "size": "150MB",
                    "status": "completed"
                },
                {
                    "backup_id": "backup_20240114_143022",
                    "created_at": "2024-01-14T14:30:22",
                    "size": "148MB",
                    "status": "completed"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            raise
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Restore from backup
        """
        try:
            # This is a placeholder - implement actual restore logic
            return {
                "backup_id": backup_id,
                "restored_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            raise
    
    def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Delete backup
        """
        try:
            # This is a placeholder - implement actual delete logic
            return {
                "backup_id": backup_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            raise 