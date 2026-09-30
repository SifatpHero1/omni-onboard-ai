from src.models.schemas import OnboardingState, ApprovalStatus
from src.tools.slack_client import SlackClient
from src.utils.logger import logger

class ApproverAgent:
    """Agent responsible for requesting human approval via Slack"""
    
    def __init__(self):
        self.slack_client = SlackClient()
    
    def request_approval(self, state: OnboardingState) -> dict:
        """Send approval request to Slack"""
        logger.info(f"⏸️ Approver Agent: Requesting approval for {state.extracted_data.company_name}")
        
        # Prepare client data for Slack message
        client_data = state.extracted_data.model_dump()
        client_data['email_id'] = state.email_id
        
        # Send approval request to Slack
        success = self.slack_client.send_approval_request(
            client_data=client_data,
            email_id=state.email_id
        )
        
        if success:
            logger.info("✅ Approval request sent to Slack")
            
            # In a real implementation, you would:
            # 1. Store the workflow state in a database
            # 2. Wait for a webhook callback from Slack
            # 3. Resume the workflow when approval is received
            
            # For demo purposes, we'll simulate approval
            # In production, this would be handled by a webhook endpoint
            logger.info("⏳ Waiting for human approval (simulated for demo)...")
            
            # Simulate approval after a delay
            # In production, this would be async with webhook
            return {
                "approval_status": ApprovalStatus.APPROVED,
                "approver": "demo_user",
                "updated_at": state.updated_at
            }
        else:
            logger.error("❌ Failed to send approval request")
            return {
                "approval_status": ApprovalStatus.REJECTED,
                "approver": "system",
                "error_message": "Failed to send approval request to Slack",
                "updated_at": state.updated_at
            }