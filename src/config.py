import os
from dotenv import load_dotenv
from pathlib import Path

# .env ফাইল লোড করা
load_dotenv()

class Config:
    """প্রজেক্টের সব কনফিগারেশন এক জায়গায়"""
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini") # খরচ কমাতে mini ব্যবহার করছি
    
    # HubSpot Configuration
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    HUBSPOT_BASE_URL = os.getenv("HUBSPOT_BASE_URL", "https://api.hubapi.com")
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/onboarding.db")
    
    @classmethod
    def validate(cls):
        """চেক করা যে প্রয়োজনীয় API Key গুলো আছে কিনা"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "sk-your-openai-api-key-here":
            print("⚠️ Warning: Valid OPENAI_API_KEY is missing in .env file!")
            return False
        return True