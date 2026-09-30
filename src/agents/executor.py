from src.models.schemas import OnboardingState
from src.tools.hubspot_client import HubSpotClient
from src.tools.email_client import EmailClient
from src.tools.slack_client import SlackClient
from src.tools.db_client import DatabaseClient
from src.utils.logger import logger

class ExecutorAgent:
    """Agent responsible for executing final actions (CRM sync, email, notifications)"""
    
    def __init__(self):
        self.hubspot_client = HubSpotClient()
        self.email_client = EmailClient()
        self.slack_client = SlackClient()
        self.db_client = DatabaseClient()
    
    def execute(self, state: OnboardingState) -> dict:
        """Execute final onboarding actions"""
        logger.info(f"⚡ Executor Agent: Executing onboarding for {state.extracted_data.company_name}")
        
        client_data = state.extracted_data.model_dump()
        
        try:
            # Step 1: Create company in HubSpot
            logger.info("Step 1: Creating company in HubSpot...")
            company_response = self.hubspot_client.create_company(client_data)
            
            if not company_response.success:
                raise Exception(f"HubSpot company creation failed: {company_response.message}")
            
            # Step 2: Create contact in HubSpot
            logger.info("Step 2: Creating contact in HubSpot...")
            contact_response = self.hubspot_client.create_contact(
                client_data,
                company_response.company_id
            )
            
            if not contact_response.success:
                raise Exception(f"HubSpot contact creation failed: {contact_response.message}")
            
            # Step 3: Insert client into local database
            logger.info("Step 3: Saving to local database...")
            self.db_client.insert_client(client_data)
            
            # Step 4: Send welcome email
            logger.info("Step 4: Sending welcome email...")
            email_success = self.email_client.send_welcome_email(client_data)
            
            if not email_success:
                logger.warning("⚠️ Welcome email failed, but continuing...")
            
            # Step 5: Send success notification to Slack
            logger.info("Step 5: Sending success notification to Slack...")
            self.slack_client.send_success_notification(client_data)
            
            # Step 6: Log to audit
            self.db_client.log_audit(
                state.email_id,
                "ONBOARDING_COMPLETED",
                f"Successfully onboarded {client_data['company_name']}"
            )
            
            logger.info(f"✅ Onboarding completed successfully for {client_data['company_name']}")
            
            return {
                "crm_response": f"Company ID: {company_response.company_id}, Contact ID: {contact_response.contact_id}",
                "email_sent": email_success,
                "updated_at": state.updated_at
            }
        
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            # Log error to audit
            self.db_client.log_audit(
                state.email_id,
                "ONBOARDING_FAILED",
                error_msg
            )
            
            return {
                "error_message": error_msg,
                "updated_at": state.updated_at
            }