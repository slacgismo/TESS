
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os



def send_email(subject, message, bcc):
    '''sendgrid email setup'''

    email_address = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('PASSWORD')
 
    message = Mail(
        from_email=email_address,
        to_emails=bcc,
        subject=message['subject'],
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e.message)
