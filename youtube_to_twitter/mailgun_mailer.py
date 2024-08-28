import requests
import logging
import os

logger = logging.getLogger(__name__)

def send_simple_summary(receiver, subject, summary):
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Excited User <mailgun@{MAILGUN_DOMAIN}>",
                "to": [receiver, f"YOU@{MAILGUN_DOMAIN}"],
                "subject": subject,
                "text": summary
            }
        )
        
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        
        logger.info(f"Email sent successfully to {receiver}. Mailgun response: {response.text}")
        return True, "Email sent successfully"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email to {receiver}. Error: {str(e)}")
        return False, f"Failed to send email: {str(e)}"