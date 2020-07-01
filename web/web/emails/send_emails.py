import smtplib
import web.emails.config as config
from email.mime.text import MIMEText

smtplib
server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(config.EMAIL_ADDRESS, config.PASSWORD)


def send_email(subject, message, bcc):
    '''Simple SMTP set up with gmail'''

    # Simple set up for basic working email functionality
    # TODO: styling email, switch to implementing OAuth/Gmail API

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')

        msg = MIMEText(message)
        msg['From'] = config.EMAIL_ADDRESS
        msg['Subject'] = subject

        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)

        server.sendmail(config.EMAIL_ADDRESS, bcc, msg.as_string())
        server.quit()

    except:
        print("email failed to send")
