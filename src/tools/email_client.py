import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from src.config import Config
from src.utils.logger import logger

class EmailClient:
    """Email client for sending welcome emails"""
    
    def __init__(self):
        self.sender_email = Config.GMAIL_SENDER_EMAIL
        self.api_key = Config.GMAIL_API_KEY
        # Note: In production, use Gmail API with OAuth2
        # For demo, we'll use SMTP (configure with your email provider)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_welcome_email(self, client_data: Dict) -> bool:
        """Send welcome email to new client"""
        
        subject = f"Welcome to Our Services, {client_data['contact_person']}!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">Welcome to Our Platform!</h2>
            
            <p>Dear {client_data['contact_person']},</p>
            
            <p>We're thrilled to welcome <strong>{client_data['company_name']}</strong> to our platform!</p>
            
            <h3>Your Subscription Details:</h3>
            <ul>
                <li><strong>Service Tier:</strong> {client_data['service_tier']}</li>
                <li><strong>Monthly Investment:</strong> ${client_data['monthly_value']:,.2f}</li>
            </ul>
            
            <h3>Next Steps:</h3>
            <ol>
                <li>Our onboarding team will contact you within 24 hours</li>
                <li>You'll receive access credentials via a separate email</li>
                <li>Schedule your kickoff meeting with your account manager</li>
            </ol>
            
            {f'<p><strong>Special Requirements Noted:</strong> {client_data["requirements"]}</p>' if client_data.get('requirements') else ''}
            
            <p>If you have any questions, please don't hesitate to reach out to us.</p>
            
            <p>Best regards,<br>
            <strong>The Onboarding Team</strong></p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                This is an automated message. Please do not reply to this email.
            </p>
        </body>
        </html>
        """
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = client_data['contact_email']
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Note: In production, use proper authentication
            # For demo purposes, we'll just log the email
            logger.info(f"Welcome email prepared for {client_data['contact_email']}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Email ID: {client_data.get('email_id', 'N/A')}")
            
            # Uncomment below for actual email sending (requires proper SMTP setup)
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.sender_email, self.api_key)
            #     server.send_message(message)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False