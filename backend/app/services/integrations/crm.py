# backend/app/services/integrations/crm.py

import logging
import requests
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Ticket, Brand, CRMIntegration
from app.schemas import TicketCreate, TicketUpdate
from app.config.settings import settings

logger = logging.getLogger(__name__)

class CRMService:
    def __init__(self, db: Session):
        self.db = db
        self.supported_crms = {
            'salesforce': SalesforceCRM,
            'zoho': ZohoCRM,
            'freshworks': FreshworksCRM,
            'kapture': KaptureCRM,
            'leadsquared': LeadSquaredCRM,
            'hubspot': HubSpotCRM,
            'pipedrive': PipedriveCRM
        }
    
    def create_ticket_in_crm(self, ticket: Ticket, brand: Brand, crm_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a ticket in the configured CRM system
        """
        try:
            crm_type = crm_config.get('crm_type')
            if crm_type not in self.supported_crms:
                raise ValueError(f"Unsupported CRM type: {crm_type}")
            
            crm_instance = self.supported_crms[crm_type](crm_config)
            result = crm_instance.create_case(ticket, brand)
            
            # Store CRM reference
            self._store_crm_reference(ticket.id, crm_type, result.get('case_id'), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating ticket in CRM: {e}")
            return {"success": False, "error": str(e)}
    
    def update_ticket_in_crm(self, ticket: Ticket, crm_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a ticket in the configured CRM system
        """
        try:
            crm_type = crm_config.get('crm_type')
            if crm_type not in self.supported_crms:
                raise ValueError(f"Unsupported CRM type: {crm_type}")
            
            crm_instance = self.supported_crms[crm_type](crm_config)
            result = crm_instance.update_case(ticket)
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating ticket in CRM: {e}")
            return {"success": False, "error": str(e)}
    
    def sync_from_crm(self, crm_config: Dict[str, Any], last_sync_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync tickets from CRM to our system
        """
        try:
            crm_type = crm_config.get('crm_type')
            if crm_type not in self.supported_crms:
                raise ValueError(f"Unsupported CRM type: {crm_type}")
            
            crm_instance = self.supported_crms[crm_type](crm_config)
            result = crm_instance.sync_cases(last_sync_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error syncing from CRM: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_crm_webhook(self, crm_type: str, webhook_data: Dict[str, Any], brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming webhooks from CRM systems for real-time updates
        """
        try:
            logger.info(f"Processing CRM webhook from {crm_type} for brand {brand_id}")
            
            if crm_type not in self.supported_crms:
                return {"success": False, "error": f"Unsupported CRM type: {crm_type}"}
            
            # Get brand's CRM configuration
            crm_integration = self.db.query(CRMIntegration).filter(
                CRMIntegration.brand_id == brand_id,
                CRMIntegration.crm_type == crm_type,
                CRMIntegration.is_active == True
            ).first()
            
            if not crm_integration:
                return {"success": False, "error": "CRM integration not found or inactive"}
            
            # Create CRM instance
            crm_instance = self.supported_crms[crm_type](crm_integration.config)
            
            # Process webhook based on CRM type
            if crm_type == 'salesforce':
                return self._handle_salesforce_webhook(webhook_data, brand_id, crm_instance)
            elif crm_type == 'zoho':
                return self._handle_zoho_webhook(webhook_data, brand_id, crm_instance)
            elif crm_type == 'freshworks':
                return self._handle_freshworks_webhook(webhook_data, brand_id, crm_instance)
            elif crm_type == 'hubspot':
                return self._handle_hubspot_webhook(webhook_data, brand_id, crm_instance)
            elif crm_type == 'pipedrive':
                return self._handle_pipedrive_webhook(webhook_data, brand_id, crm_instance)
            else:
                return self._handle_generic_webhook(webhook_data, brand_id, crm_instance)
                
        except Exception as e:
            logger.error(f"Error handling CRM webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_salesforce_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle Salesforce webhook updates"""
        try:
            # Extract case information from Salesforce webhook
            case_data = webhook_data.get('sobject', {})
            case_id = case_data.get('Id')
            status = case_data.get('Status')
            subject = case_data.get('Subject')
            description = case_data.get('Description')
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(case_id)
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for Salesforce case {case_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on Salesforce changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if subject and subject != ticket.title:
                updates['title'] = subject
            if description and description != ticket.description:
                updates['description'] = description
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from Salesforce webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling Salesforce webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_zoho_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle Zoho webhook updates"""
        try:
            # Extract ticket information from Zoho webhook
            ticket_data = webhook_data.get('ticket', {})
            ticket_id = ticket_data.get('id')
            status = ticket_data.get('status')
            subject = ticket_data.get('subject')
            description = ticket_data.get('description')
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(str(ticket_id))
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for Zoho ticket {ticket_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on Zoho changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if subject and subject != ticket.title:
                updates['title'] = subject
            if description and description != ticket.description:
                updates['description'] = description
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from Zoho webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling Zoho webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_freshworks_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle Freshworks webhook updates"""
        try:
            # Extract ticket information from Freshworks webhook
            ticket_data = webhook_data.get('ticket', {})
            ticket_id = ticket_data.get('id')
            status = ticket_data.get('status')
            subject = ticket_data.get('subject')
            description = ticket_data.get('description')
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(str(ticket_id))
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for Freshworks ticket {ticket_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on Freshworks changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if subject and subject != ticket.title:
                updates['title'] = subject
            if description and description != ticket.description:
                updates['description'] = description
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from Freshworks webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling Freshworks webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_hubspot_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle HubSpot webhook updates"""
        try:
            # Extract ticket information from HubSpot webhook
            ticket_data = webhook_data.get('ticket', {})
            ticket_id = ticket_data.get('id')
            status = ticket_data.get('hs_ticket_status')
            subject = ticket_data.get('subject')
            description = ticket_data.get('content')
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(str(ticket_id))
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for HubSpot ticket {ticket_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on HubSpot changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if subject and subject != ticket.title:
                updates['title'] = subject
            if description and description != ticket.description:
                updates['description'] = description
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from HubSpot webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling HubSpot webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_pipedrive_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle Pipedrive webhook updates"""
        try:
            # Extract deal information from Pipedrive webhook
            deal_data = webhook_data.get('deal', {})
            deal_id = deal_data.get('id')
            status = deal_data.get('status')
            title = deal_data.get('title')
            value = deal_data.get('value')
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(str(deal_id))
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for Pipedrive deal {deal_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on Pipedrive changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if title and title != ticket.title:
                updates['title'] = title
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from Pipedrive webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling Pipedrive webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_generic_webhook(self, webhook_data: Dict[str, Any], brand_id: int, crm_instance) -> Dict[str, Any]:
        """Handle generic webhook updates for unsupported CRM types"""
        try:
            # Try to extract common fields
            ticket_id = webhook_data.get('ticket_id') or webhook_data.get('id') or webhook_data.get('case_id')
            status = webhook_data.get('status') or webhook_data.get('state')
            subject = webhook_data.get('subject') or webhook_data.get('title')
            description = webhook_data.get('description') or webhook_data.get('content')
            
            if not ticket_id:
                return {"success": False, "error": "No ticket ID found in webhook data"}
            
            # Find corresponding ticket
            ticket = self.db.query(Ticket).filter(
                Ticket.brand_id == brand_id,
                Ticket.crm_reference.contains(str(ticket_id))
            ).first()
            
            if not ticket:
                logger.warning(f"Ticket not found for generic webhook ticket {ticket_id}")
                return {"success": False, "error": "Ticket not found"}
            
            # Update ticket based on webhook changes
            updates = {}
            if status and status != ticket.status:
                updates['status'] = status
            if subject and subject != ticket.title:
                updates['title'] = subject
            if description and description != ticket.description:
                updates['description'] = description
            
            if updates:
                for field, value in updates.items():
                    setattr(ticket, field, value)
                ticket.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated ticket {ticket.id} from generic webhook")
            
            return {"success": True, "ticket_id": ticket.id, "updates": updates}
            
        except Exception as e:
            logger.error(f"Error handling generic webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_webhook_signature(self, webhook_data: str, signature: str, secret: str) -> bool:
        """Verify webhook signature for security"""
        try:
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                webhook_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
<<<<<<< HEAD
    def _store_crm_reference(self, ticket_id: int, crm_type: str, crm_id: str, meta_data: Dict[str, Any]):
=======
    def _store_crm_reference(self, ticket_id: int, crm_type: str, crm_id: str, metadata: Dict[str, Any]):
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        """Store CRM reference in ticket"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.crm_reference = json.dumps({
                    "crm_type": crm_type,
                    "crm_id": crm_id,
<<<<<<< HEAD
                    "meta_data": meta_data,
=======
                    "metadata": metadata,
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
                    "synced_at": datetime.utcnow().isoformat()
                })
                self.db.commit()
                logger.info(f"Stored CRM reference for ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Error storing CRM reference: {e}")

class BaseCRM:
    """Base class for CRM integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for CRM"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        """Create case in CRM - to be implemented by subclasses"""
        raise NotImplementedError
    
    def update_case(self, ticket: Ticket) -> Dict[str, Any]:
        """Update case in CRM - to be implemented by subclasses"""
        raise NotImplementedError
    
    def sync_cases(self, last_sync_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Sync cases from CRM - to be implemented by subclasses"""
        raise NotImplementedError
    
    def process_webhook(self, webhook_data: Dict[str, Any], brand_id: int, db: Session) -> Dict[str, Any]:
        """Process webhook from CRM - to be implemented by subclasses"""
        raise NotImplementedError

class SalesforceCRM(BaseCRM):
    """Salesforce Service Cloud integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/services/data/v58.0/sobjects/Case"
            
            case_data = {
                "Subject": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "Description": ticket.content,
                "Priority": self._map_priority(ticket.severity),
                "Status": self._map_status(ticket.status),
                "Origin": self._map_channel(ticket.channel),
                "Type": "Complaint",
                "AccountId": brand.crm_account_id if hasattr(brand, 'crm_account_id') else None,
                "ContactId": self._get_contact_id(ticket.user_identifier),
                "Custom_Field_1__c": ticket.id,  # Store our ticket ID
                "Custom_Field_2__c": ticket.channel
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "case_number": result.get('caseNumber'),
                    "message": "Case created successfully in Salesforce"
                }
            else:
                return {
                    "success": False,
                    "error": f"Salesforce API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating Salesforce case: {e}")
            return {"success": False, "error": str(e)}
    
    def update_case(self, ticket: Ticket) -> Dict[str, Any]:
        try:
            # Get CRM reference
            crm_ref = self.db.query(CRMIntegration).filter(
                CRMIntegration.ticket_id == ticket.id,
                CRMIntegration.crm_type == 'salesforce'
            ).first()
            
            if not crm_ref:
                return {"success": False, "error": "No CRM reference found"}
            
            url = f"{self.base_url}/services/data/v58.0/sobjects/Case/{crm_ref.crm_case_id}"
            
            update_data = {
                "Status": self._map_status(ticket.status),
                "Description": ticket.content
            }
            
            response = requests.patch(url, headers=self.headers, json=update_data)
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "Case updated successfully in Salesforce"
                }
            else:
                return {
                    "success": False,
                    "error": f"Salesforce API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error updating Salesforce case: {e}")
            return {"success": False, "error": str(e)}
    
    def _map_priority(self, severity: str) -> str:
        mapping = {
            'low': 'Low',
            'medium': 'Medium', 
            'high': 'High',
            'critical': 'High'
        }
        return mapping.get(severity.lower(), 'Medium')
    
    def _map_status(self, status: str) -> str:
        mapping = {
            'new': 'New',
            'progress': 'In Progress',
            'resolved': 'Closed'
        }
        return mapping.get(status.lower(), 'New')
    
    def _map_channel(self, channel: str) -> str:
        mapping = {
            'whatsapp': 'Social',
            'telegram': 'Social',
            'instagram': 'Social',
            'linkedin': 'Social',
            'webchat': 'Web',
            'voice': 'Phone',
            'sms': 'SMS'
        }
        return mapping.get(channel.lower(), 'Web')
    
    def _get_contact_id(self, user_identifier: str) -> Optional[str]:
        # This would typically query Salesforce for existing contact
        # For now, return None to create anonymous case
        return None

class ZohoCRM(BaseCRM):
    """Zoho Desk integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/tickets"
            
            case_data = {
                "subject": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "description": ticket.content,
                "priority": self._map_priority(ticket.severity),
                "status": self._map_status(ticket.status),
                "channel": self._map_channel(ticket.channel),
                "classification": "Complaint",
                "cf_ticket_id": ticket.id,
                "cf_channel": ticket.channel
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "ticket_number": result.get('ticketNumber'),
                    "message": "Ticket created successfully in Zoho Desk"
                }
            else:
                return {
                    "success": False,
                    "error": f"Zoho API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating Zoho ticket: {e}")
            return {"success": False, "error": str(e)}
    
    def update_case(self, ticket: Ticket) -> Dict[str, Any]:
        try:
            crm_ref = self.db.query(CRMIntegration).filter(
                CRMIntegration.ticket_id == ticket.id,
                CRMIntegration.crm_type == 'zoho'
            ).first()
            
            if not crm_ref:
                return {"success": False, "error": "No CRM reference found"}
            
            url = f"{self.base_url}/api/v1/tickets/{crm_ref.crm_case_id}"
            
            update_data = {
                "status": self._map_status(ticket.status),
                "description": ticket.content
            }
            
            response = requests.put(url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Ticket updated successfully in Zoho Desk"
                }
            else:
                return {
                    "success": False,
                    "error": f"Zoho API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error updating Zoho ticket: {e}")
            return {"success": False, "error": str(e)}
    
    def _map_priority(self, severity: str) -> str:
        mapping = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High', 
            'critical': 'Urgent'
        }
        return mapping.get(severity.lower(), 'Medium')
    
    def _map_status(self, status: str) -> str:
        mapping = {
            'new': 'Open',
            'progress': 'In Progress',
            'resolved': 'Closed'
        }
        return mapping.get(status.lower(), 'Open')
    
    def _map_channel(self, channel: str) -> str:
        mapping = {
            'whatsapp': 'WhatsApp',
            'telegram': 'Telegram',
            'instagram': 'Instagram',
            'linkedin': 'LinkedIn',
            'webchat': 'Web',
            'voice': 'Phone',
            'sms': 'SMS'
        }
        return mapping.get(channel.lower(), 'Web')

class FreshworksCRM(BaseCRM):
    """Freshdesk/Freshworks integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v2/tickets"
            
            case_data = {
                "subject": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "description": ticket.content,
                "priority": self._map_priority(ticket.severity),
                "status": self._map_status(ticket.status),
                "source": self._map_channel(ticket.channel),
                "type": "Complaint",
                "custom_fields": {
                    "cf_ticket_id": ticket.id,
                    "cf_channel": ticket.channel
                }
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "ticket_number": result.get('ticket_id'),
                    "message": "Ticket created successfully in Freshdesk"
                }
            else:
                return {
                    "success": False,
                    "error": f"Freshdesk API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating Freshdesk ticket: {e}")
            return {"success": False, "error": str(e)}
    
    def update_case(self, ticket: Ticket) -> Dict[str, Any]:
        try:
            crm_ref = self.db.query(CRMIntegration).filter(
                CRMIntegration.ticket_id == ticket.id,
                CRMIntegration.crm_type == 'freshworks'
            ).first()
            
            if not crm_ref:
                return {"success": False, "error": "No CRM reference found"}
            
            url = f"{self.base_url}/api/v2/tickets/{crm_ref.crm_case_id}"
            
            update_data = {
                "status": self._map_status(ticket.status),
                "description": ticket.content
            }
            
            response = requests.put(url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Ticket updated successfully in Freshdesk"
                }
            else:
                return {
                    "success": False,
                    "error": f"Freshdesk API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error updating Freshdesk ticket: {e}")
            return {"success": False, "error": str(e)}
    
    def _map_priority(self, severity: str) -> int:
        mapping = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return mapping.get(severity.lower(), 2)
    
    def _map_status(self, status: str) -> int:
        mapping = {
            'new': 2,  # Open
            'progress': 3,  # Pending
            'resolved': 5  # Closed
        }
        return mapping.get(status.lower(), 2)
    
    def _map_channel(self, channel: str) -> int:
        mapping = {
            'whatsapp': 1,  # Portal
            'telegram': 1,
            'instagram': 1,
            'linkedin': 1,
            'webchat': 1,
            'voice': 2,  # Phone
            'sms': 3  # Email
        }
        return mapping.get(channel.lower(), 1)

class KaptureCRM(BaseCRM):
    """Kapture CRM integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/tickets"
            
            case_data = {
                "title": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "description": ticket.content,
                "priority": self._map_priority(ticket.severity),
                "status": self._map_status(ticket.status),
                "source": self._map_channel(ticket.channel),
                "category": "Complaint",
                "custom_fields": {
                    "ticket_id": ticket.id,
                    "channel": ticket.channel
                }
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "ticket_number": result.get('ticket_number'),
                    "message": "Ticket created successfully in Kapture CRM"
                }
            else:
                return {
                    "success": False,
                    "error": f"Kapture API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating Kapture ticket: {e}")
            return {"success": False, "error": str(e)}

class LeadSquaredCRM(BaseCRM):
    """LeadSquared CRM integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/activities"
            
            case_data = {
                "activityType": "Complaint",
                "title": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "description": ticket.content,
                "priority": self._map_priority(ticket.severity),
                "status": self._map_status(ticket.status),
                "source": self._map_channel(ticket.channel),
                "customFields": {
                    "ticket_id": ticket.id,
                    "channel": ticket.channel
                }
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "activity_id": result.get('activityId'),
                    "message": "Activity created successfully in LeadSquared"
                }
            else:
                return {
                    "success": False,
                    "error": f"LeadSquared API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating LeadSquared activity: {e}")
            return {"success": False, "error": str(e)}

class HubSpotCRM(BaseCRM):
    """HubSpot CRM integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/crm/v3/objects/tickets"
            
            case_data = {
                "properties": {
                    "subject": f"Complaint: {ticket.title or 'Customer Complaint'}",
                    "content": ticket.content,
                    "hs_ticket_priority": self._map_priority(ticket.severity),
                    "hs_ticket_category": "Complaint",
                    "hs_pipeline": "0",
                    "hs_pipeline_stage": self._map_status(ticket.status),
                    "ticket_id": str(ticket.id),
                    "channel": ticket.channel
                }
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('id'),
                    "ticket_number": result.get('properties', {}).get('hs_ticket_id'),
                    "message": "Ticket created successfully in HubSpot"
                }
            else:
                return {
                    "success": False,
                    "error": f"HubSpot API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating HubSpot ticket: {e}")
            return {"success": False, "error": str(e)}

class PipedriveCRM(BaseCRM):
    """Pipedrive CRM integration"""
    
    def create_case(self, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/v1/deals"
            
            case_data = {
                "title": f"Complaint: {ticket.title or 'Customer Complaint'}",
                "value": 0,
                "currency": "USD",
                "stage_id": self._map_status(ticket.status),
                "note": ticket.content,
                "custom_fields": {
                    "ticket_id": ticket.id,
                    "channel": ticket.channel,
                    "priority": ticket.severity
                }
            }
            
            response = requests.post(url, headers=self.headers, json=case_data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "case_id": result.get('data', {}).get('id'),
                    "deal_id": result.get('data', {}).get('id'),
                    "message": "Deal created successfully in Pipedrive"
                }
            else:
                return {
                    "success": False,
                    "error": f"Pipedrive API error: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating Pipedrive deal: {e}")
            return {"success": False, "error": str(e)}
