from src.models.schemas import OnboardingState, ValidationStatus, ValidationResult
from src.tools.db_client import DatabaseClient
from src.utils.logger import logger

class ValidatorAgent:
    """Agent responsible for validating extracted client data"""
    
    def __init__(self):
        self.db_client = DatabaseClient()
    
    def validate(self, state: OnboardingState) -> dict:
        """Validate the extracted client data"""
        logger.info(f"🔍 Validator Agent: Validating data for email {state.email_id}")
        
        if not state.extracted_data:
            logger.error("❌ No extracted data to validate")
            return {
                "validation_status": ValidationStatus.FAILED,
                "validation_message": "No data extracted from email"
            }
        
        data = state.extracted_data
        validation_errors = []
        
        # Validation Rule 1: Check if company already exists
        if self.db_client.check_company_exists(data.company_name):
            validation_errors.append(f"Company '{data.company_name}' already exists in our system")
        
        # Validation Rule 2: Check monthly value
        if data.monthly_value <= 0:
            validation_errors.append("Monthly value must be greater than 0")
        
        # Validation Rule 3: Check email format (already validated by Pydantic)
        if not data.contact_email or '@' not in data.contact_email:
            validation_errors.append("Invalid email address")
        
        # Validation Rule 4: Check company name length
        if len(data.company_name) < 2:
            validation_errors.append("Company name is too short")
        
        # Validation Rule 5: Check service tier
        if data.service_tier not in ["Basic", "Pro", "Enterprise"]:
            validation_errors.append(f"Invalid service tier: {data.service_tier}")
        
        # Determine validation status
        if validation_errors:
            error_message = "Validation failed: " + "; ".join(validation_errors)
            logger.warning(f"⚠️ {error_message}")
            
            # Log to audit
            self.db_client.log_audit(
                state.email_id,
                "VALIDATION_FAILED",
                error_message
            )
            
            return {
                "validation_status": ValidationStatus.FAILED,
                "validation_message": error_message,
                "updated_at": state.updated_at
            }
        
        # All validations passed
        logger.info(f"✅ Validation passed for {data.company_name}")
        
        # Log to audit
        self.db_client.log_audit(
            state.email_id,
            "VALIDATION_PASSED",
            f"Data validated successfully for {data.company_name}"
        )
        
        return {
            "validation_status": ValidationStatus.PASSED,
            "validation_message": "All validations passed",
            "updated_at": state.updated_at
        }