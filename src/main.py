from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from datetime import datetime

from src.models.schemas import OnboardingState, ClientData, ValidationStatus, ApprovalStatus
from src.agents.extractor import ExtractorAgent
from src.agents.validator import ValidatorAgent
from src.agents.approver import ApproverAgent
from src.agents.executor import ExecutorAgent
from src.utils.logger import logger
from src.config import Config

# Define the workflow state
class WorkflowState(TypedDict):
    email_id: str
    email_subject: str
    email_body: str
    extracted_data: dict | None
    validation_status: str
    validation_message: str | None
    approval_status: str
    approver: str | None
    crm_response: str | None
    email_sent: bool
    error_message: str | None
    created_at: datetime
    updated_at: datetime

# Initialize agents
extractor = ExtractorAgent(use_anthropic=False)
validator = ValidatorAgent()
approver = ApproverAgent()
executor = ExecutorAgent()

# Define workflow nodes
def extract_node(state: WorkflowState) -> dict:
    """Extract data from email"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Client Onboarding Workflow")
    logger.info("=" * 60)
    
    # Convert to Pydantic model for agent
    pydantic_state = OnboardingState(
        email_id=state['email_id'],
        email_subject=state['email_subject'],
        email_body=state['email_body'],
        created_at=state['created_at'],
        updated_at=state['updated_at']
    )
    
    result = extractor.extract(pydantic_state)
    
    return {
        "extracted_data": result.get("extracted_data"),
        "error_message": result.get("error_message"),
        "updated_at": datetime.utcnow()
    }

def validate_node(state: WorkflowState) -> dict:
    """Validate extracted data"""
    # Convert to Pydantic model
    pydantic_state = OnboardingState(
        email_id=state['email_id'],
        email_subject=state['email_subject'],
        email_body=state['email_body'],
        extracted_data=ClientData(**state['extracted_data']) if state.get('extracted_data') else None,
        created_at=state['created_at'],
        updated_at=state['updated_at']
    )
    
    result = validator.validate(pydantic_state)
    
    return {
        "validation_status": result.get("validation_status"),
        "validation_message": result.get("validation_message"),
        "updated_at": datetime.utcnow()
    }

def approve_node(state: WorkflowState) -> dict:
    """Request human approval"""
    # Convert to Pydantic model
    pydantic_state = OnboardingState(
        email_id=state['email_id'],
        email_subject=state['email_subject'],
        email_body=state['email_body'],
        extracted_data=ClientData(**state['extracted_data']) if state.get('extracted_data') else None,
        validation_status=ValidationStatus(state['validation_status']),
        created_at=state['created_at'],
        updated_at=state['updated_at']
    )
    
    result = approver.request_approval(pydantic_state)
    
    return {
        "approval_status": result.get("approval_status"),
        "approver": result.get("approver"),
        "error_message": result.get("error_message"),
        "updated_at": datetime.utcnow()
    }

def execute_node(state: WorkflowState) -> dict:
    """Execute final onboarding actions"""
    # Convert to Pydantic model
    pydantic_state = OnboardingState(
        email_id=state['email_id'],
        email_subject=state['email_subject'],
        email_body=state['email_body'],
        extracted_data=ClientData(**state['extracted_data']) if state.get('extracted_data') else None,
        validation_status=ValidationStatus(state['validation_status']),
        approval_status=ApprovalStatus(state['approval_status']),
        created_at=state['created_at'],
        updated_at=state['updated_at']
    )
    
    result = executor.execute(pydantic_state)
    
    return {
        "crm_response": result.get("crm_response"),
        "email_sent": result.get("email_sent", False),
        "error_message": result.get("error_message"),
        "updated_at": datetime.utcnow()
    }

# Define routing functions
def should_continue_after_validation(state: WorkflowState) -> Literal["approve", "end"]:
    """Route based on validation result"""
    if state['validation_status'] == ValidationStatus.PASSED:
        logger.info("✅ Validation passed, proceeding to approval")
        return "approve"
    else:
        logger.warning(f"❌ Validation failed: {state['validation_message']}")
        return "end"

def should_continue_after_approval(state: WorkflowState) -> Literal["execute", "end"]:
    """Route based on approval result"""
    if state['approval_status'] == ApprovalStatus.APPROVED:
        logger.info("✅ Approved, proceeding to execution")
        return "execute"
    else:
        logger.warning(f"❌ Rejected by {state['approver']}")
        return "end"

# Build the workflow graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("extract", extract_node)
workflow.add_node("validate", validate_node)
workflow.add_node("approve", approve_node)
workflow.add_node("execute", execute_node)

# Set entry point
workflow.set_entry_point("extract")

# Add edges
workflow.add_edge("extract", "validate")
workflow.add_conditional_edges(
    "validate",
    should_continue_after_validation,
    {
        "approve": "approve",
        "end": END
    }
)
workflow.add_conditional_edges(
    "approve",
    should_continue_after_approval,
    {
        "execute": "execute",
        "end": END
    }
)
workflow.add_edge("execute", END)

# Compile the workflow
app = workflow.compile()

def run_workflow(email_id: str, email_subject: str, email_body: str) -> dict:
    """Run the complete onboarding workflow"""
    
    # Initialize state
    initial_state = WorkflowState(
        email_id=email_id,
        email_subject=email_subject,
        email_body=email_body,
        extracted_data=None,
        validation_status=ValidationStatus.PENDING,
        validation_message=None,
        approval_status=ApprovalStatus.PENDING,
        approver=None,
        crm_response=None,
        email_sent=False,
        error_message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Run workflow
    final_state = app.invoke(initial_state)
    
    # Log final result
    logger.info("=" * 60)
    logger.info("📊 Workflow Summary")
    logger.info("=" * 60)
    logger.info(f"Email ID: {final_state['email_id']}")
    logger.info(f"Validation: {final_state['validation_status']}")
    logger.info(f"Approval: {final_state['approval_status']}")
    logger.info(f"CRM Response: {final_state['crm_response'] or 'N/A'}")
    logger.info(f"Email Sent: {final_state['email_sent']}")
    if final_state['error_message']:
        logger.error(f"Error: {final_state['error_message']}")
    logger.info("=" * 60)
    
    return final_state

if __name__ == "__main__":
    # Validate configuration
    Config.validate()
    
    # Example usage
    test_email = {
        "email_id": "EMAIL_001",
        "email_subject": "New Client Onboarding Request - TechCorp Inc.",
        "email_body": """
        Hi,
        
        We are TechCorp Inc. and we would like to sign up for your Pro tier service.
        
        Contact Person: John Doe
        Email: john.doe@techcorp.com
        Expected Monthly Budget: $5,000
        
        Special Requirements: We need API access and priority support.
        
        Looking forward to working with you!
        
        Best regards,
        John Doe
        TechCorp Inc.
        """
    }
    
    result = run_workflow(**test_email)