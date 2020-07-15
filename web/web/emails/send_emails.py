import smtplib
from dotenv import load_dotenv
load_dotenv()

import os
from email.mime.text import MIMEText

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('PASSWORD')

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()


def send_email(subject, message, bcc):
    '''Simple SMTP set up with gmail'''

    print("hello")
    # Simple set up for basic working email functionality
    # TODO: styling email, switch to implementing OAuth/Gmail API

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')

        msg = MIMEText(message)
        msg['From'] = EMAIL_ADDRESS
        msg['Subject'] = subject

        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, PASSWORD)

        server.sendmail(EMAIL_ADDRESS, bcc, msg.as_string())
        server.quit()

    except:
        print("email failed to send")
