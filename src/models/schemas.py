from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ServiceTier(str, Enum):
    """Service tier enumeration"""
    BASIC = "Basic"
    PRO = "Pro"
    ENTERPRISE = "Enterprise"

class ValidationStatus(str, Enum):
    """Validation status enumeration"""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"

class ApprovalStatus(str, Enum):
    """Approval status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ClientData(BaseModel):
    """Structured client data extracted from email"""
    company_name: str = Field(description="Name of the client company")
    contact_person: str = Field(description="Primary contact person name")
    contact_email: EmailStr = Field(description="Primary contact email address")
    service_tier: ServiceTier = Field(description="Requested service tier")
    monthly_value: float = Field(description="Expected monthly revenue in USD")
    requirements: Optional[str] = Field(default=None, description="Special requirements or notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "TechCorp Inc.",
                "contact_person": "John Doe",
                "contact_email": "john@techcorp.com",
                "service_tier": "Pro",
                "monthly_value": 5000.00,
                "requirements": "Need API access"
            }
        }

class OnboardingState(BaseModel):
    """State object for the LangGraph workflow"""
    email_id: str = Field(description="Unique email identifier")
    email_body: str = Field(description="Raw email content")
    email_subject: str = Field(description="Email subject line")
    extracted_data: Optional[ClientData] = Field(default=None, description="Extracted client data")
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING)
    validation_message: Optional[str] = Field(default=None, description="Validation result message")
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    approver: Optional[str] = Field(default=None, description="Person who approved/rejected")
    crm_response: Optional[str] = Field(default=None, description="CRM sync response")
    email_sent: bool = Field(default=False, description="Whether welcome email was sent")
    error_message: Optional[str] = Field(default=None, description="Error message if any")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ValidationResult(BaseModel):
    """Result of data validation"""
    status: ValidationStatus
    message: str
    details: Optional[dict] = None

class CRMResponse(BaseModel):
    """Response from CRM sync"""
    success: bool
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    message: str