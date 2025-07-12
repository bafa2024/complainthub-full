# backend/app/services/telephony.py

import logging
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import PhoneNumber, TelephonyProvider, PhoneNumberRequest, Brand
from app.schemas import PhoneNumberCreate, AvailableNumber
from app.config.settings import settings
import hashlib
import hmac

logger = logging.getLogger(__name__)

class TelephonyService:
    def __init__(self, db: Session):
        self.db = db
        self.providers = {
            "twilio": TwilioProvider(),
            "knowlarity": KnowlarityProvider(),
            "exotel": ExotelProvider(),
            "ozonetel": OzonetelProvider(),
            "myoperator": MyOperatorProvider()
        }
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available telephony providers"""
        return [
            {
                "name": "twilio",
                "display_name": "Twilio",
                "supported_countries": ["US", "IN", "GB", "CA", "AU"],
                "supported_capabilities": ["voice", "sms", "whatsapp"],
                "pricing": {
                    "toll-free": {"monthly": 1.0, "setup": 0.0},
                    "local": {"monthly": 1.0, "setup": 0.0}
                }
            },
            {
                "name": "knowlarity",
                "display_name": "Knowlarity",
                "supported_countries": ["IN"],
                "supported_capabilities": ["voice", "sms"],
                "pricing": {
                    "toll-free": {"monthly": 500.0, "setup": 0.0},
                    "local": {"monthly": 100.0, "setup": 0.0}
                }
            },
            {
                "name": "exotel",
                "display_name": "Exotel",
                "supported_countries": ["IN"],
                "supported_capabilities": ["voice", "sms"],
                "pricing": {
                    "toll-free": {"monthly": 500.0, "setup": 0.0},
                    "local": {"monthly": 100.0, "setup": 0.0}
                }
            },
            {
                "name": "ozonetel",
                "display_name": "Ozonetel",
                "supported_countries": ["IN"],
                "supported_capabilities": ["voice", "sms"],
                "pricing": {
                    "toll-free": {"monthly": 500.0, "setup": 0.0},
                    "local": {"monthly": 100.0, "setup": 0.0}
                }
            },
            {
                "name": "myoperator",
                "display_name": "MyOperator",
                "supported_countries": ["IN"],
                "supported_capabilities": ["voice", "sms"],
                "pricing": {
                    "toll-free": {"monthly": 500.0, "setup": 0.0},
                    "local": {"monthly": 100.0, "setup": 0.0}
                }
            }
        ]
    
    def search_available_numbers(self, country_code: str = "IN", 
                               number_type: str = "toll-free",
                               capabilities: List[str] = None,
                               provider: str = None) -> List[AvailableNumber]:
        """Search for available phone numbers across providers"""
        available_numbers = []
        
        if capabilities is None:
            capabilities = ["voice", "sms"]
        
        providers_to_search = [provider] if provider else self.providers.keys()
        
        for provider_name in providers_to_search:
            if provider_name not in self.providers:
                continue
                
            try:
                provider_numbers = self.providers[provider_name].search_numbers(
                    country_code=country_code,
                    number_type=number_type,
                    capabilities=capabilities
                )
                available_numbers.extend(provider_numbers)
            except Exception as e:
                logger.error(f"Error searching numbers from {provider_name}: {e}")
                continue
        
        return available_numbers
    
    def purchase_number(self, phone_number: str, provider: str, 
                       brand_id: int, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a phone number from a provider"""
        try:
            if provider not in self.providers:
                return {"success": False, "error": f"Provider {provider} not supported"}
            
            # Purchase from provider
            result = self.providers[provider].purchase_number(
                phone_number=phone_number,
                capabilities=capabilities
            )
            
            if not result["success"]:
                return result
            
            # Create phone number record in database
            phone_number_data = PhoneNumberCreate(
                brand_id=brand_id,
                phone_number=phone_number,
                provider=provider,
                provider_id=result.get("provider_id"),
                country_code=result.get("country_code", "IN"),
                number_type=result.get("number_type", "toll-free"),
                capabilities={"voice": "voice" in capabilities, "sms": "sms" in capabilities},
                monthly_cost=result.get("monthly_cost", 0.0),
                setup_cost=result.get("setup_cost", 0.0),
                webhook_url=f"{settings.FRONTEND_URL}/api/v1/webhook/{provider}"
            )
            
            db_phone_number = PhoneNumber(**phone_number_data.dict())
            self.db.add(db_phone_number)
            self.db.commit()
            self.db.refresh(db_phone_number)
            
            return {
                "success": True,
                "phone_number": phone_number,
                "provider": provider,
                "monthly_cost": result.get("monthly_cost", 0.0),
                "setup_cost": result.get("setup_cost", 0.0),
                "webhook_url": db_phone_number.webhook_url
            }
            
        except Exception as e:
            logger.error(f"Error purchasing number {phone_number}: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str) -> Dict[str, Any]:
        """Release a phone number back to the provider"""
        try:
            # Find phone number in database
            db_phone_number = self.db.query(PhoneNumber).filter(
                PhoneNumber.phone_number == phone_number
            ).first()
            
            if not db_phone_number:
                return {"success": False, "error": "Phone number not found"}
            
            # Release from provider
            if db_phone_number.provider in self.providers:
                result = self.providers[db_phone_number.provider].release_number(
                    phone_number=phone_number,
                    provider_id=db_phone_number.provider_id
                )
                
                if not result["success"]:
                    return result
            
            # Update status in database
            db_phone_number.status = "inactive"
            self.db.commit()
            
            return {"success": True, "message": f"Number {phone_number} released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing number {phone_number}: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_brand_numbers(self, brand_id: int) -> List[PhoneNumber]:
        """Get all phone numbers for a brand"""
        return self.db.query(PhoneNumber).filter(
            PhoneNumber.brand_id == brand_id
        ).all()
    
    def get_number_requests(self, brand_id: int) -> List[PhoneNumberRequest]:
        """Get all phone number requests for a brand"""
        return self.db.query(PhoneNumberRequest).filter(
            PhoneNumberRequest.brand_id == brand_id
        ).order_by(PhoneNumberRequest.created_at.desc()).all()


class BaseProvider:
    """Base class for telephony providers"""
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available numbers - to be implemented by subclasses"""
        raise NotImplementedError
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a number - to be implemented by subclasses"""
        raise NotImplementedError
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release a number - to be implemented by subclasses"""
        raise NotImplementedError


class TwilioProvider(BaseProvider):
    """Twilio telephony provider implementation"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.base_url = "https://api.twilio.com/2010-04-01"
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available Twilio numbers"""
        if not self.account_sid or not self.auth_token:
            return []
        
        try:
            # Convert capabilities to Twilio format
            voice_enabled = "voice" in capabilities
            sms_enabled = "sms" in capabilities
            
            # Search for available numbers
            url = f"{self.base_url}/Accounts/{self.account_sid}/AvailablePhoneNumbers/{country_code}/Local.json"
            
            params = {
                "VoiceEnabled": voice_enabled,
                "SmsEnabled": sms_enabled,
                "Limit": 20
            }
            
            response = requests.get(url, params=params, auth=(self.account_sid, self.auth_token))
            
            if response.status_code == 200:
                data = response.json()
                numbers = []
                
                for number_data in data.get("available_phone_numbers", []):
                    numbers.append(AvailableNumber(
                        phone_number=number_data["phone_number"],
                        provider="twilio",
                        country_code=country_code,
                        number_type=number_type,
                        capabilities=capabilities,
                        monthly_cost=1.0,
                        setup_cost=0.0,
                        features=["voice", "sms"] if voice_enabled and sms_enabled else capabilities
                    ))
                
                return numbers
            else:
                logger.error(f"Twilio API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Twilio numbers: {e}")
            return []
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a Twilio number"""
        if not self.account_sid or not self.auth_token:
            return {"success": False, "error": "Twilio credentials not configured"}
        
        try:
            # Extract country code from phone number
            country_code = "US" if phone_number.startswith("+1") else "IN"
            
            # Purchase the number
            url = f"{self.base_url}/Accounts/{self.account_sid}/IncomingPhoneNumbers.json"
            
            data = {
                "PhoneNumber": phone_number,
                "VoiceUrl": f"{settings.FRONTEND_URL}/api/v1/webhook/voice",
                "SmsUrl": f"{settings.FRONTEND_URL}/api/v1/webhook/sms"
            }
            
            response = requests.post(url, data=data, auth=(self.account_sid, self.auth_token))
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "provider_id": result["sid"],
                    "country_code": country_code,
                    "number_type": "local",
                    "monthly_cost": 1.0,
                    "setup_cost": 0.0
                }
            else:
                logger.error(f"Twilio purchase error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"Failed to purchase number: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error purchasing Twilio number: {e}")
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release a Twilio number"""
        if not self.account_sid or not self.auth_token:
            return {"success": False, "error": "Twilio credentials not configured"}
        
        try:
            url = f"{self.base_url}/Accounts/{self.account_sid}/IncomingPhoneNumbers/{provider_id}.json"
            response = requests.delete(url, auth=(self.account_sid, self.auth_token))
            
            if response.status_code == 204:
                return {"success": True, "message": "Number released successfully"}
            else:
                return {"success": False, "error": f"Failed to release number: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error releasing Twilio number: {e}")
            return {"success": False, "error": str(e)}


class KnowlarityProvider(BaseProvider):
    """Knowlarity telephony provider implementation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'KNOWLARITY_API_KEY', '')
        self.base_url = "https://api.knowlarity.com/v1"
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available Knowlarity numbers"""
        if not self.api_key:
            return []
        
        try:
            # Mock implementation - in real scenario, call Knowlarity API
            numbers = []
            
            # Generate some mock toll-free numbers
            for i in range(5):
                numbers.append(AvailableNumber(
                    phone_number=f"+91-1800-{1000+i:04d}",
                    provider="knowlarity",
                    country_code="IN",
                    number_type="toll-free",
                    capabilities=capabilities,
                    monthly_cost=500.0,
                    setup_cost=0.0,
                    features=capabilities
                ))
            
            return numbers
            
        except Exception as e:
            logger.error(f"Error searching Knowlarity numbers: {e}")
            return []
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a Knowlarity number"""
        if not self.api_key:
            return {"success": False, "error": "Knowlarity API key not configured"}
        
        try:
            # Mock implementation
            return {
                "success": True,
                "provider_id": f"knowlarity_{phone_number.replace('+', '').replace('-', '')}",
                "country_code": "IN",
                "number_type": "toll-free",
                "monthly_cost": 500.0,
                "setup_cost": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error purchasing Knowlarity number: {e}")
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release a Knowlarity number"""
        if not self.api_key:
            return {"success": False, "error": "Knowlarity API key not configured"}
        
        try:
            # Mock implementation
            return {"success": True, "message": "Number released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing Knowlarity number: {e}")
            return {"success": False, "error": str(e)}


class ExotelProvider(BaseProvider):
    """Exotel telephony provider implementation"""
    
    def __init__(self):
        self.sid = getattr(settings, 'EXOTEL_SID', '')
        self.token = getattr(settings, 'EXOTEL_TOKEN', '')
        self.base_url = "https://api.exotel.com/v1"
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available Exotel numbers"""
        if not self.sid or not self.token:
            return []
        
        try:
            # Mock implementation
            numbers = []
            
            for i in range(5):
                numbers.append(AvailableNumber(
                    phone_number=f"+91-1800-{2000+i:04d}",
                    provider="exotel",
                    country_code="IN",
                    number_type="toll-free",
                    capabilities=capabilities,
                    monthly_cost=500.0,
                    setup_cost=0.0,
                    features=capabilities
                ))
            
            return numbers
            
        except Exception as e:
            logger.error(f"Error searching Exotel numbers: {e}")
            return []
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase an Exotel number"""
        if not self.sid or not self.token:
            return {"success": False, "error": "Exotel credentials not configured"}
        
        try:
            # Mock implementation
            return {
                "success": True,
                "provider_id": f"exotel_{phone_number.replace('+', '').replace('-', '')}",
                "country_code": "IN",
                "number_type": "toll-free",
                "monthly_cost": 500.0,
                "setup_cost": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error purchasing Exotel number: {e}")
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release an Exotel number"""
        if not self.sid or not self.token:
            return {"success": False, "error": "Exotel credentials not configured"}
        
        try:
            # Mock implementation
            return {"success": True, "message": "Number released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing Exotel number: {e}")
            return {"success": False, "error": str(e)}


class OzonetelProvider(BaseProvider):
    """Ozonetel telephony provider implementation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OZONETEL_API_KEY', '')
        self.base_url = "https://api.ozonetel.com/v1"
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available Ozonetel numbers"""
        if not self.api_key:
            return []
        
        try:
            # Mock implementation
            numbers = []
            
            for i in range(5):
                numbers.append(AvailableNumber(
                    phone_number=f"+91-1800-{3000+i:04d}",
                    provider="ozonetel",
                    country_code="IN",
                    number_type="toll-free",
                    capabilities=capabilities,
                    monthly_cost=500.0,
                    setup_cost=0.0,
                    features=capabilities
                ))
            
            return numbers
            
        except Exception as e:
            logger.error(f"Error searching Ozonetel numbers: {e}")
            return []
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase an Ozonetel number"""
        if not self.api_key:
            return {"success": False, "error": "Ozonetel API key not configured"}
        
        try:
            # Mock implementation
            return {
                "success": True,
                "provider_id": f"ozonetel_{phone_number.replace('+', '').replace('-', '')}",
                "country_code": "IN",
                "number_type": "toll-free",
                "monthly_cost": 500.0,
                "setup_cost": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error purchasing Ozonetel number: {e}")
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release an Ozonetel number"""
        if not self.api_key:
            return {"success": False, "error": "Ozonetel API key not configured"}
        
        try:
            # Mock implementation
            return {"success": True, "message": "Number released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing Ozonetel number: {e}")
            return {"success": False, "error": str(e)}


class MyOperatorProvider(BaseProvider):
    """MyOperator telephony provider implementation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'MYOPERATOR_API_KEY', '')
        self.base_url = "https://api.myoperator.co/v1"
    
    def search_numbers(self, country_code: str, number_type: str, 
                      capabilities: List[str]) -> List[AvailableNumber]:
        """Search for available MyOperator numbers"""
        if not self.api_key:
            return []
        
        try:
            # Mock implementation
            numbers = []
            
            for i in range(5):
                numbers.append(AvailableNumber(
                    phone_number=f"+91-1800-{4000+i:04d}",
                    provider="myoperator",
                    country_code="IN",
                    number_type="toll-free",
                    capabilities=capabilities,
                    monthly_cost=500.0,
                    setup_cost=0.0,
                    features=capabilities
                ))
            
            return numbers
            
        except Exception as e:
            logger.error(f"Error searching MyOperator numbers: {e}")
            return []
    
    def purchase_number(self, phone_number: str, capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a MyOperator number"""
        if not self.api_key:
            return {"success": False, "error": "MyOperator API key not configured"}
        
        try:
            # Mock implementation
            return {
                "success": True,
                "provider_id": f"myoperator_{phone_number.replace('+', '').replace('-', '')}",
                "country_code": "IN",
                "number_type": "toll-free",
                "monthly_cost": 500.0,
                "setup_cost": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error purchasing MyOperator number: {e}")
            return {"success": False, "error": str(e)}
    
    def release_number(self, phone_number: str, provider_id: str) -> Dict[str, Any]:
        """Release a MyOperator number"""
        if not self.api_key:
            return {"success": False, "error": "MyOperator API key not configured"}
        
        try:
            # Mock implementation
            return {"success": True, "message": "Number released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing MyOperator number: {e}")
            return {"success": False, "error": str(e)} 