import requests
from typing import Dict, Optional
from src.config import Config
from src.utils.logger import logger
from src.models.schemas import CRMResponse

class HubSpotClient:
    """HubSpot CRM client for company and contact management"""
    
    def __init__(self):
        self.api_key = Config.HUBSPOT_API_KEY
        self.base_url = Config.HUBSPOT_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_company(self, company_data: Dict) -> CRMResponse:
        """Create a new company in HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/companies"
        
        payload = {
            "properties": {
                "name": company_data['company_name'],
                "domain": self._extract_domain(company_data['contact_email']),
                "description": f"Service Tier: {company_data['service_tier']}",
                "annualrevenue": company_data['monthly_value'] * 12,
                "lifecyclestage": "customer"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            company_id = result.get('id')
            
            logger.info(f"Created company in HubSpot: {company_data['company_name']} (ID: {company_id})")
            
            return CRMResponse(
                success=True,
                company_id=company_id,
                message=f"Company created successfully with ID: {company_id}"
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create company in HubSpot: {str(e)}")
            return CRMResponse(
                success=False,
                message=f"Failed to create company: {str(e)}"
            )
    
    def create_contact(self, contact_data: Dict, company_id: str) -> CRMResponse:
        """Create a new contact in HubSpot and associate with company"""
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        payload = {
            "properties": {
                "email": contact_data['contact_email'],
                "firstname": contact_data['contact_person'].split()[0],
                "lastname": " ".join(contact_data['contact_person'].split()[1:]) if len(contact_data['contact_person'].split()) > 1 else "",
                "company": contact_data['company_name']
            }
        }
        
        try:
            # Create contact
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            contact_id = result.get('id')
            
            # Associate contact with company
            association_url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}/associations/company/{company_id}/contact_to_company"
            requests.put(association_url, headers=self.headers)
            
            logger.info(f"Created contact in HubSpot: {contact_data['contact_email']} (ID: {contact_id})")
            
            return CRMResponse(
                success=True,
                contact_id=contact_id,
                message=f"Contact created and associated with company successfully"
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create contact in HubSpot: {str(e)}")
            return CRMResponse(
                success=False,
                message=f"Failed to create contact: {str(e)}"
            )
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address"""
        return email.split('@')[1] if '@' in email else ""