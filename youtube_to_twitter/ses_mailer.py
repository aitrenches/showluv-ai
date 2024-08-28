import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# Replace these with your actual Amazon SES SMTP details
SMTP_ENDPOINT = 'email-smtp.us-east-2.amazonaws.com'
SMTP_USERNAME = 'AKIATYE4PMZ7WWBIM2RX'
SMTP_PASSWORD = 'BMQdkCWy0qQo1vB5PAuLySNL®gNMjdr8tc3ppSZuq+/8'
SENDER_EMAIL = 'oliko@trenches.ai'
SENDER_NAME = 'TRENCHES AI'

def send_summary_email(receiver, subject, summary):
    try:
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = formataddr((SENDER_NAME, SENDER_EMAIL))
        message['To'] = receiver
        message['Subject'] = subject

        # Add the summary to the email body with UTF-8 encoding
        message.attach(MIMEText(summary, 'plain', 'utf-8'))

        # Create SMTP session for sending the mail
        session = smtplib.SMTP(SMTP_ENDPOINT, 587)
        session.starttls()  # Secure the connection
        session.login(SMTP_USERNAME, SMTP_PASSWORD)  # Login with SMTP credentials

        # Convert the message to a string and send the email
        text = message.as_string()
        session.sendmail(SENDER_EMAIL, receiver, text.encode('utf-8'))
        session.quit()

        return True, "Email sent successfully"
    
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"