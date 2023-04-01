import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings

class GmailService:
    __instance = None

    def __init__(self):
        self.email = settings.MAIL_SERVICE_EMAIL
        self.password = settings.MAIL_PASSWORD
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def send_email(self, to_email: str, subject: str, body: str):
        message = MIMEMultipart()
        message['From'] = self.email
        message['To'] = to_email
        message['Subject'] = subject
        body = MIMEText(body)
        message.attach(body)

        smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_server.starttls()
        smtp_server.login(self.email, self.password)
        smtp_server.sendmail(self.email, to_email, message.as_string())
        smtp_server.quit()