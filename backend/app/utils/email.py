from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from email.mime.text import MIMEText
import os
import base64

sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

def send_daily_report(to_email: str, subject: str, content: str, attachment_path: str = None):
    """
    Send DSM report email with optional PDF/Excel attachment.
    """
    message = Mail(
        from_email='noreply@sprngenergy.com',
        to_emails=to_email,
        subject=subject,
        html_content=content  # HTML summary, e.g., <table> of DSM data
    )
    
    if attachment_path:
        with open(attachment_path, 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment(
            FileContent(encoded),
            FileName(os.path.basename(attachment_path)),
            FileType('application/pdf'),  # Or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' for Excel
            Disposition('attachment')
        )
        message.attachment = attachment
    
    try:
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Email send error: {e}")
        return False
