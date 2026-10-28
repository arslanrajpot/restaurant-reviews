import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config_project.config import settings
from restaurants import repository
from users.model import Tier

def send_email(receiver_email: str, subject: str, message: str):
    """
    Send an email using SMTP
    
    Args:
        receiver_email (str): Email address of the recipient
        subject (str): Subject of the email
        message (str): HTML content of the email
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_EMAIL
    msg['To'] = receiver_email

    # Attach the HTML message
    msg.attach(MIMEText(message, 'html'))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise


def store_competitor_data(competitor_info, pinecone_uploader):
    """Store single competitor data and return upload count"""
    competitor, all_reviews_data = competitor_info
    competitor_data = competitor.get('basic_data', {})
    competitor_name = competitor.get('name', '')
    competitor_reviews = all_reviews_data.get(competitor_name, [])

    if competitor_data:
        try:
            # Store competitor in database
            stored_competitor = repository.create_restaurant_from_search(competitor_data, competitor_reviews)

            # Upload to RAG
            competitor_rag_count = pinecone_uploader.upload_search_data(competitor_data, competitor_reviews)

            print(f"✅ Stored {competitor_name} (RAG: {competitor_rag_count})")
            return 1, competitor_rag_count
        except Exception as e:
            print(f" Error storing {competitor_name}: {str(e)}")
            return 0, 0
    return 0, 0


def get_payment_failed_email_content(customer_email):
    subject = "Payment Failed: Action Needed for Your Subscription"
    message = f"""
    <html>
    <body>
        <p>Dear {customer_email.split('@')[0]},</p>
        <p>We were unable to process your latest subscription payment. Your plan is still active and we will retry the payment automatically over the next few days.</p>
        <p>Please make sure your card is valid and has sufficient funds. If the payment keeps failing, your subscription will be cancelled and your account moved to the Free tier.</p>
        <p>Thank you!</p> 
        <p style="color: #a87b02; font-weight: bold; font-size: 18px; margin-top: 0;">ReviewPulse</p>
    </body>
    </html>
    """
    return subject, message

def get_tier_from_price_id(price_id: str) -> Tier:
    """Stripe price ID to user tier"""
    price_tier_mapping = {
        settings.PRO_PRICE_ID: Tier.PRO,
        settings.PREMIUM_PRICE_ID: Tier.PREMIUM,  
    }
    return price_tier_mapping.get(price_id, Tier.FREE)