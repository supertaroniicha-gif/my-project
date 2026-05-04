#!/usr/bin/env python3
import requests
from datetime import datetime
from anthropic import Anthropic

# Initialize Anthropic client for web search via Claude
client = Anthropic()

def fetch_semiconductor_news():
    """Fetch latest semiconductor and Micron Technology news"""
    try:
        # Use Anthropic API with web search to find latest news
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1500,
            tools=[
                {
                    "type": "web_search",
                    "name": "search",
                    "description": "Search the web for information"
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": "Find the latest 5 news articles about Micron Technology stock price, earnings, and semiconductor market trends from the past week. Include the source and date for each article."
                }
            ]
        )

        # Extract the search results
        news_content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                news_content += block.text

        return news_content
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def format_email_body(news_content):
    """Format the news into a nice email body"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = f"""
📊 Semiconductor Market & Micron Technology News
================================================

Date: {timestamp}

{news_content}

---
This is an automated daily semiconductor news digest.
Focus: Micron Technology stock price, earnings, and market trends.
"""

    return body

def create_news_email(recipient_email):
    """Create a draft Gmail with the news"""
    try:
        news = fetch_semiconductor_news()
        email_body = format_email_body(news)

        # Import the Gmail tool - this will be called by Claude Code
        print("=" * 60)
        print("EMAIL CONTENT TO SEND:")
        print("=" * 60)
        print(f"To: {recipient_email}")
        print(f"Subject: Daily Semiconductor News - Micron Technology Update")
        print("\n" + email_body)
        print("=" * 60)

        return {
            "status": "ready",
            "to": recipient_email,
            "subject": "Daily Semiconductor News - Micron Technology Update",
            "body": email_body
        }
    except Exception as e:
        print(f"Error creating email: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import sys

    # Get email from command line or use default
    email = sys.argv[1] if len(sys.argv) > 1 else "user@gmail.com"

    result = create_news_email(email)
    if result["status"] == "ready":
        print(f"\n✅ Email ready to send to {email}")
    else:
        print(f"❌ {result.get('error', 'Unknown error')}")
