# backend/app/services/email_outreach_service.py

import logging
import requests
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import Brand, Ticket, EmailOutreachLog
from app.services.notifications import send_email
from app.core.ai_engine import AIEngine
from app.config.settings import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import time
import random

logger = logging.getLogger(__name__)

class EmailOutreachService:
    """
    Automated Email Outreach Service
    
    Features:
    - Web scraping for brand support contacts
    - Automated email outreach campaigns
    - Contact discovery and validation
    - Email template management
    - Outreach tracking and analytics
    - Rate limiting and compliance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
        
        # Email outreach configuration
        self.config = {
            "max_emails_per_day": 100,
            "rate_limit_delay": 2,  # seconds between emails
            "max_retries": 3,
            "outreach_retention_days": 365,
            "contact_discovery_timeout": 30,
            "email_validation_timeout": 10
        }
        
        # User agents for web scraping
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
    
    def discover_brand_contacts(self, brand_name: str, website_url: str = None) -> Dict[str, Any]:
        """
        Discover support contacts for a brand through web scraping
        """
        try:
            logger.info(f"Starting contact discovery for brand: {brand_name}")
            
            contacts = {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": [],
                "social_media": [],
                "discovered_at": datetime.utcnow().isoformat()
            }
            
            # If website URL is provided, scrape it
            if website_url:
                website_contacts = self._scrape_website_contacts(website_url)
                contacts.update(website_contacts)
            
            # Search for brand contact information
            search_contacts = self._search_brand_contacts(brand_name)
            contacts.update(search_contacts)
            
            # Validate discovered contacts
            validated_contacts = self._validate_contacts(contacts)
            
            logger.info(f"Contact discovery completed for {brand_name}: {len(validated_contacts['support_emails'])} emails found")
            
            return {
                "success": True,
                "brand_name": brand_name,
                "contacts": validated_contacts,
                "discovery_methods": ["web_scraping", "search_engines"]
            }
            
        except Exception as e:
            logger.error(f"Error discovering contacts for brand {brand_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _scrape_website_contacts(self, website_url: str) -> Dict[str, Any]:
        """
        Scrape contact information from a website
        """
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            response = requests.get(
                website_url, 
                headers=headers, 
                timeout=self.config["contact_discovery_timeout"],
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            contacts = {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": [],
                "social_media": []
            }
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, response.text)
            
            # Filter for support-related emails
            support_keywords = ['support', 'help', 'contact', 'service', 'customer', 'care']
            for email in emails:
                email_lower = email.lower()
                if any(keyword in email_lower for keyword in support_keywords):
                    contacts["support_emails"].append(email)
            
            # Extract phone numbers
            phone_pattern = r'[\+]?[1-9][\d]{0,15}'
            phones = re.findall(phone_pattern, response.text)
            contacts["support_phones"] = list(set(phones))[:5]  # Limit to 5 unique numbers
            
            # Find contact forms
            contact_forms = soup.find_all('form')
            for form in contact_forms:
                form_action = form.get('action', '')
                if any(keyword in form_action.lower() for keyword in ['contact', 'support', 'help']):
                    contacts["contact_forms"].append({
                        "action": form_action,
                        "method": form.get('method', 'POST')
                    })
            
            # Find social media links
            social_patterns = [
                r'facebook\.com/[^"\s]+',
                r'twitter\.com/[^"\s]+',
                r'linkedin\.com/[^"\s]+',
                r'instagram\.com/[^"\s]+'
            ]
            
            for pattern in social_patterns:
                social_links = re.findall(pattern, response.text)
                contacts["social_media"].extend(social_links)
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error scraping website {website_url}: {e}")
            return {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": [],
                "social_media": []
            }
    
    def _search_brand_contacts(self, brand_name: str) -> Dict[str, Any]:
        """
        Search for brand contact information using search engines
        """
        try:
            contacts = {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": [],
                "social_media": []
            }
            
            # Search queries for contact discovery
            search_queries = [
                f'"{brand_name}" "support email"',
                f'"{brand_name}" "contact us"',
                f'"{brand_name}" "customer service"',
                f'"{brand_name}" "help desk"'
            ]
            
            for query in search_queries:
                try:
                    # This would integrate with a search API (Google, Bing, etc.)
                    # For now, we'll simulate the search
                    logger.info(f"Searching for: {query}")
                    
                    # Simulate search results
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error searching for query '{query}': {e}")
                    continue
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error searching for brand contacts: {e}")
            return {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": [],
                "social_media": []
            }
    
    def _validate_contacts(self, contacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate discovered contact information
        """
        try:
            validated_contacts = {
                "support_emails": [],
                "support_phones": [],
                "contact_forms": contacts.get("contact_forms", []),
                "social_media": contacts.get("social_media", [])
            }
            
            # Validate email addresses
            for email in contacts.get("support_emails", []):
                if self._validate_email(email):
                    validated_contacts["support_emails"].append(email)
            
            # Validate phone numbers
            for phone in contacts.get("support_phones", []):
                if self._validate_phone(phone):
                    validated_contacts["support_phones"].append(phone)
            
            return validated_contacts
            
        except Exception as e:
            logger.error(f"Error validating contacts: {e}")
            return contacts
    
    def _validate_email(self, email: str) -> bool:
        """
        Basic email validation
        """
        try:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False
    
    def _validate_phone(self, phone: str) -> bool:
        """
        Basic phone number validation
        """
        try:
            # Remove non-digit characters
            digits_only = re.sub(r'\D', '', phone)
            return len(digits_only) >= 10
        except Exception:
            return False
    
    def send_outreach_email(
        self, 
        brand_id: int, 
        contact_email: str, 
        email_type: str = "partnership",
        custom_message: str = None
    ) -> Dict[str, Any]:
        """
        Send outreach email to brand support contact
        """
        try:
            logger.info(f"Sending outreach email to {contact_email} for brand {brand_id}")
            
            # Get brand details
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Check rate limiting
            if not self._check_rate_limit(brand_id):
                return {"success": False, "error": "Rate limit exceeded"}
            
            # Generate email content
            email_content = self._generate_outreach_email(
                brand_name=brand.name,
                contact_email=contact_email,
                email_type=email_type,
                custom_message=custom_message
            )
            
            # Send email
            success = send_email(
                to_email=contact_email,
                subject=email_content["subject"],
                html_content=email_content["html_content"],
                text_content=email_content["text_content"]
            )
            
            # Log outreach attempt
            outreach_log = EmailOutreachLog(
                brand_id=brand_id,
                contact_email=contact_email,
                email_type=email_type,
                subject=email_content["subject"],
                message=email_content["text_content"],
                status="sent" if success else "failed",
                sent_at=datetime.utcnow()
            )
            
            self.db.add(outreach_log)
            self.db.commit()
            
            if success:
                logger.info(f"Successfully sent outreach email to {contact_email}")
                return {
                    "success": True,
                    "message": "Outreach email sent successfully",
                    "outreach_id": outreach_log.id
                }
            else:
                logger.warning(f"Failed to send outreach email to {contact_email}")
                return {
                    "success": False,
                    "error": "Failed to send email",
                    "outreach_id": outreach_log.id
                }
            
        except Exception as e:
            logger.error(f"Error sending outreach email: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_outreach_email(
        self, 
        brand_name: str, 
        contact_email: str, 
        email_type: str,
        custom_message: str = None
    ) -> Dict[str, str]:
        """
        Generate outreach email content
        """
        try:
            if email_type == "partnership":
                subject = f"Partnership Opportunity - {brand_name} & ComplaintHub"
                template = self._get_partnership_template()
            elif email_type == "integration":
                subject = f"Integration Opportunity - {brand_name} & ComplaintHub"
                template = self._get_integration_template()
            elif email_type == "custom":
                subject = f"Business Inquiry - {brand_name}"
                template = self._get_custom_template()
            else:
                subject = f"Business Inquiry - {brand_name}"
                template = self._get_general_template()
            
            # Replace placeholders
            html_content = template["html"].format(
                brand_name=brand_name,
                contact_email=contact_email,
                custom_message=custom_message or "",
                current_date=datetime.utcnow().strftime("%B %d, %Y")
            )
            
            text_content = template["text"].format(
                brand_name=brand_name,
                contact_email=contact_email,
                custom_message=custom_message or "",
                current_date=datetime.utcnow().strftime("%B %d, %Y")
            )
            
            return {
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content
            }
            
        except Exception as e:
            logger.error(f"Error generating outreach email: {e}")
            return {
                "subject": f"Business Inquiry - {brand_name}",
                "html_content": f"<p>Hello,</p><p>This is a business inquiry from ComplaintHub.</p>",
                "text_content": f"Hello,\n\nThis is a business inquiry from ComplaintHub."
            }
    
    def _get_partnership_template(self) -> Dict[str, str]:
        """
        Get partnership outreach email template
        """
        return {
            "html": """
            <html>
            <body>
                <h2>Partnership Opportunity - ComplaintHub & {brand_name}</h2>
                <p>Dear {brand_name} Team,</p>
                <p>I hope this email finds you well. I'm reaching out from ComplaintHub, a leading AI-powered complaint management platform that helps brands streamline their customer service operations.</p>
                <p>We've noticed that {brand_name} is committed to excellent customer service, and we believe there's a great opportunity for collaboration.</p>
                <p><strong>What we offer:</strong></p>
                <ul>
                    <li>AI-powered complaint classification and routing</li>
                    <li>Multi-channel support (WhatsApp, Telegram, Voice, Email)</li>
                    <li>Automated follow-up and resolution tracking</li>
                    <li>Comprehensive analytics and reporting</li>
                    <li>24/7 automated customer support</li>
                </ul>
                <p><strong>Partnership Benefits:</strong></p>
                <ul>
                    <li>Reduced response times by up to 80%</li>
                    <li>Improved customer satisfaction scores</li>
                    <li>Cost savings through automation</li>
                    <li>Scalable support infrastructure</li>
                </ul>
                {custom_message}
                <p>Would you be interested in a brief call to discuss how ComplaintHub could benefit {brand_name}?</p>
                <p>Best regards,<br>The ComplaintHub Team</p>
                <p><small>Sent on {current_date}</small></p>
            </body>
            </html>
            """,
            "text": """
            Partnership Opportunity - ComplaintHub & {brand_name}

            Dear {brand_name} Team,

            I hope this email finds you well. I'm reaching out from ComplaintHub, a leading AI-powered complaint management platform that helps brands streamline their customer service operations.

            We've noticed that {brand_name} is committed to excellent customer service, and we believe there's a great opportunity for collaboration.

            What we offer:
            - AI-powered complaint classification and routing
            - Multi-channel support (WhatsApp, Telegram, Voice, Email)
            - Automated follow-up and resolution tracking
            - Comprehensive analytics and reporting
            - 24/7 automated customer support

            Partnership Benefits:
            - Reduced response times by up to 80%
            - Improved customer satisfaction scores
            - Cost savings through automation
            - Scalable support infrastructure

            {custom_message}

            Would you be interested in a brief call to discuss how ComplaintHub could benefit {brand_name}?

            Best regards,
            The ComplaintHub Team

            Sent on {current_date}
            """
        }
    
    def _get_integration_template(self) -> Dict[str, str]:
        """
        Get integration outreach email template
        """
        return {
            "html": """
            <html>
            <body>
                <h2>Integration Opportunity - ComplaintHub & {brand_name}</h2>
                <p>Dear {brand_name} Team,</p>
                <p>I hope this email finds you well. I'm reaching out from ComplaintHub regarding a potential integration opportunity.</p>
                <p>We've developed a comprehensive API that can seamlessly integrate with {brand_name}'s existing systems to enhance your customer service capabilities.</p>
                <p><strong>Integration Benefits:</strong></p>
                <ul>
                    <li>Seamless data synchronization</li>
                    <li>Unified customer support dashboard</li>
                    <li>Automated ticket creation and updates</li>
                    <li>Real-time status tracking</li>
                    <li>Enhanced reporting capabilities</li>
                </ul>
                {custom_message}
                <p>Would you be interested in exploring this integration opportunity?</p>
                <p>Best regards,<br>The ComplaintHub Team</p>
                <p><small>Sent on {current_date}</small></p>
            </body>
            </html>
            """,
            "text": """
            Integration Opportunity - ComplaintHub & {brand_name}

            Dear {brand_name} Team,

            I hope this email finds you well. I'm reaching out from ComplaintHub regarding a potential integration opportunity.

            We've developed a comprehensive API that can seamlessly integrate with {brand_name}'s existing systems to enhance your customer service capabilities.

            Integration Benefits:
            - Seamless data synchronization
            - Unified customer support dashboard
            - Automated ticket creation and updates
            - Real-time status tracking
            - Enhanced reporting capabilities

            {custom_message}

            Would you be interested in exploring this integration opportunity?

            Best regards,
            The ComplaintHub Team

            Sent on {current_date}
            """
        }
    
    def _get_custom_template(self) -> Dict[str, str]:
        """
        Get custom outreach email template
        """
        return {
            "html": """
            <html>
            <body>
                <h2>Business Inquiry - ComplaintHub & {brand_name}</h2>
                <p>Dear {brand_name} Team,</p>
                <p>I hope this email finds you well.</p>
                {custom_message}
                <p>Best regards,<br>The ComplaintHub Team</p>
                <p><small>Sent on {current_date}</small></p>
            </body>
            </html>
            """,
            "text": """
            Business Inquiry - ComplaintHub & {brand_name}

            Dear {brand_name} Team,

            I hope this email finds you well.

            {custom_message}

            Best regards,
            The ComplaintHub Team

            Sent on {current_date}
            """
        }
    
    def _get_general_template(self) -> Dict[str, str]:
        """
        Get general outreach email template
        """
        return {
            "html": """
            <html>
            <body>
                <h2>Business Inquiry - ComplaintHub & {brand_name}</h2>
                <p>Dear {brand_name} Team,</p>
                <p>I hope this email finds you well. I'm reaching out from ComplaintHub to discuss potential business opportunities.</p>
                <p>We specialize in AI-powered complaint management solutions and would love to explore how we can help {brand_name} enhance its customer service operations.</p>
                <p>Would you be interested in a brief conversation about this opportunity?</p>
                <p>Best regards,<br>The ComplaintHub Team</p>
                <p><small>Sent on {current_date}</small></p>
            </body>
            </html>
            """,
            "text": """
            Business Inquiry - ComplaintHub & {brand_name}

            Dear {brand_name} Team,

            I hope this email finds you well. I'm reaching out from ComplaintHub to discuss potential business opportunities.

            We specialize in AI-powered complaint management solutions and would love to explore how we can help {brand_name} enhance its customer service operations.

            Would you be interested in a brief conversation about this opportunity?

            Best regards,
            The ComplaintHub Team

            Sent on {current_date}
            """
        }
    
    def _check_rate_limit(self, brand_id: int) -> bool:
        """
        Check if brand has exceeded daily email limit
        """
        try:
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            # Count emails sent today
            emails_sent_today = self.db.query(EmailOutreachLog).filter(
                and_(
                    EmailOutreachLog.brand_id == brand_id,
                    EmailOutreachLog.sent_at >= today_start,
                    EmailOutreachLog.sent_at <= today_end,
                    EmailOutreachLog.status == "sent"
                )
            ).count()
            
            return emails_sent_today < self.config["max_emails_per_day"]
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    def get_outreach_analytics(self, brand_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get outreach analytics for a brand
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get outreach logs
            outreach_logs = self.db.query(EmailOutreachLog).filter(
                and_(
                    EmailOutreachLog.brand_id == brand_id,
                    EmailOutreachLog.sent_at >= start_date
                )
            ).all()
            
            # Calculate analytics
            total_sent = len(outreach_logs)
            successful_sends = len([log for log in outreach_logs if log.status == "sent"])
            success_rate = (successful_sends / total_sent * 100) if total_sent > 0 else 0
            
            # Group by email type
            by_type = {}
            for log in outreach_logs:
                email_type = log.email_type
                if email_type not in by_type:
                    by_type[email_type] = {"sent": 0, "successful": 0}
                by_type[email_type]["sent"] += 1
                if log.status == "sent":
                    by_type[email_type]["successful"] += 1
            
            return {
                "success": True,
                "analytics": {
                    "total_sent": total_sent,
                    "successful_sends": successful_sends,
                    "success_rate": round(success_rate, 2),
                    "by_type": by_type,
                    "period_days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting outreach analytics: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_outreach_logs(self, days: int = 365) -> Dict[str, Any]:
        """
        Clean up old outreach logs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Find old logs
            old_logs = self.db.query(EmailOutreachLog).filter(
                EmailOutreachLog.sent_at < cutoff_date
            ).all()
            
            deleted_count = 0
            for log in old_logs:
                try:
                    self.db.delete(log)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting outreach log {log.id}: {e}")
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old outreach logs")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up outreach logs: {e}")
            return {"success": False, "error": str(e)} 