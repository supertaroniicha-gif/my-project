import functions_framework
import json
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from google.api_core.gapic_v1 import client_info
import google.auth.httplib2
from googleapiclient.discovery import build

# For local testing
RECIPIENT_EMAIL = "supertaroniicha@gmail.com"

def fetch_semiconductor_news_summary():
    """Generate news summary for semiconductor market"""
    return {
        "micron_stock": {
            "headline": "Micron Technology Market Updates",
            "summary": "Latest Micron Technology stock price and earnings information",
            "source": "Financial Data Provider",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        "semiconductor_market": {
            "headline": "Global Semiconductor Industry Trends",
            "summary": "Market analysis and industry trends for semiconductor sector",
            "source": "Market Research",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        "memory_prices": {
            "headline": "Memory Chip Pricing Trends",
            "summary": "DRAM and NAND pricing updates and market dynamics",
            "source": "Industry Reports",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    }

def format_email_body(news_data):
    """Format news into email body"""
    body = f"""📊 Daily Semiconductor Market & Micron Technology News Digest
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🎯 MICRON TECHNOLOGY FOCUS:
─────────────────────────
Headline: {news_data['micron_stock']['headline']}
Summary: {news_data['micron_stock']['summary']}
Source: {news_data['micron_stock']['source']} | Date: {news_data['micron_stock']['date']}

💹 SEMICONDUCTOR MARKET TRENDS:
──────────────────────────────
Headline: {news_data['semiconductor_market']['headline']}
Summary: {news_data['semiconductor_market']['summary']}
Source: {news_data['semiconductor_market']['source']} | Date: {news_data['semiconductor_market']['date']}

💾 MEMORY PRICING UPDATE:
────────────────────────
Headline: {news_data['memory_prices']['headline']}
Summary: {news_data['memory_prices']['summary']}
Source: {news_data['memory_prices']['source']} | Date: {news_data['memory_prices']['date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated daily semiconductor news digest.
Focus: Micron Technology stock price, earnings, and market trends.
"""
    return body

def create_gmail_draft(service, to_email, subject, body):
    """Create a Gmail draft using the Gmail API"""
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {'message': {'raw': raw_message}}

    draft = service.users().drafts().create(userId='me', body=draft_body).execute()
    return draft['id']

@functions_framework.http
def send_semiconductor_news(request):
    """HTTP Cloud Function to send semiconductor news

    Trigger: Cloud Scheduler at 08:00 UTC daily (configurable timezone)
    """

    try:
        # Fetch news data
        news_data = fetch_semiconductor_news_summary()
        email_body = format_email_body(news_data)

        # Get Gmail service (uses default application credentials)
        credentials = service_account.Credentials.from_service_account_file(
            'service_account_key.json',
            scopes=['https://www.googleapis.com/auth/gmail.compose']
        )

        service = build('gmail', 'v1', credentials=credentials)

        # Create the email draft
        draft_id = create_gmail_draft(
            service,
            RECIPIENT_EMAIL,
            'Daily Semiconductor News - Micron Technology Update',
            email_body
        )

        return {
            'status': 'success',
            'message': f'Email draft created with ID: {draft_id}',
            'timestamp': datetime.now().isoformat()
        }, 200

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500
