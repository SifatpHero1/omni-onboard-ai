from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict
from src.config import Config
from src.utils.logger import logger

class SlackClient:
    """Slack client for sending approval requests"""
    
    def __init__(self):
        self.client = WebClient(token=Config.SLACK_BOT_TOKEN)
        self.channel_id = Config.SLACK_CHANNEL_ID
    
    def send_approval_request(self, client_data: Dict, email_id: str) -> bool:
        """Send an interactive approval request to Slack"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 New Client Onboarding Request",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Company:*\n{client_data['company_name']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Contact:*\n{client_data['contact_person']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{client_data['contact_email']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Service Tier:*\n{client_data['service_tier']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Monthly Value:*\n${client_data['monthly_value']:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email ID:*\n{email_id}"
                    }
                ]
            }
        ]
        
        # Add requirements if present
        if client_data.get('requirements'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Special Requirements:*\n{client_data['requirements']}"
                }
            })
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Approve"
                    },
                    "style": "primary",
                    "value": f"approve_{email_id}",
                    "action_id": "approve_action"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Reject"
                    },
                    "style": "danger",
                    "value": f"reject_{email_id}",
                    "action_id": "reject_action"
                }
            ]
        })
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"New onboarding request for {client_data['company_name']}"
            )
            
            logger.info(f"Sent approval request to Slack for {client_data['company_name']}")
            return True
        
        except SlackApiError as e:
            logger.error(f"Failed to send Slack message: {e.response['error']}")
            return False
    
    def send_success_notification(self, client_data: Dict):
        """Send success notification after onboarding"""
        message = (
            f"✅ *Client Onboarded Successfully!*\n\n"
            f"Company: {client_data['company_name']}\n"
            f"Contact: {client_data['contact_person']} ({client_data['contact_email']})\n"
            f"Service Tier: {client_data['service_tier']}\n"
            f"Monthly Value: ${client_data['monthly_value']:,.2f}\n\n"
            f"Welcome email has been sent to the client."
        )
        
        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            logger.info(f"Sent success notification for {client_data['company_name']}")
        except SlackApiError as e:
            logger.error(f"Failed to send success notification: {e.response['error']}")