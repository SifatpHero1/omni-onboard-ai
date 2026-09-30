from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from src.config import Config
from src.models.schemas import ClientData, OnboardingState
from src.utils.logger import logger

class ExtractorAgent:
    """Agent responsible for extracting structured data from emails"""
    
    def __init__(self, use_anthropic: bool = False):
        if use_anthropic:
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=Config.LLM_TEMPERATURE,
                anthropic_api_key=Config.ANTHROPIC_API_KEY
            )
        else:
            self.llm = ChatOpenAI(
                model=Config.LLM_MODEL,
                temperature=Config.LLM_TEMPERATURE,
                api_key=Config.OPENAI_API_KEY
            )
        
        # Use structured output for reliable extraction
        self.structured_llm = self.llm.with_structured_output(ClientData)
    
    def extract(self, state: OnboardingState) -> dict:
        """Extract client data from email content"""
        logger.info(f"🤖 Extractor Agent: Processing email {state.email_id}")
        
        # Create extraction prompt
        prompt = f"""
        Extract client information from the following email.
        
        Email Subject: {state.email_subject}
        Email Body: {state.email_body}
        
        Extract the following fields:
        - Company name
        - Contact person name
        - Contact email address
        - Service tier (Basic, Pro, or Enterprise)
        - Monthly value (numeric, in USD)
        - Any special requirements or notes
        
        If any field is not explicitly mentioned, make a reasonable inference based on context.
        If you cannot determine a required field, use null.
        """
        
        try:
            # Extract structured data
            extracted_data = self.structured_llm.invoke(prompt)
            
            logger.info(f"✅ Extracted data for: {extracted_data.company_name}")
            
            # Update state
            state.extracted_data = extracted_data
            state.updated_at = state.updated_at
            
            return {
                "extracted_data": extracted_data.model_dump(),
                "updated_at": state.updated_at
            }
        
        except Exception as e:
            logger.error(f"❌ Extraction failed: {str(e)}")
            state.error_message = f"Extraction failed: {str(e)}"
            return {"error_message": str(e)}