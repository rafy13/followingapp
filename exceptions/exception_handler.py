from fastapi import Request
from fastapi.templating import Jinja2Templates
from smtplib import SMTPAuthenticationError

templates = Jinja2Templates(directory="templates")

def smtp_exception_handler(request: Request, exc: SMTPAuthenticationError):
    return templates.TemplateResponse(
        "common/error.html", {
            "request": request,
            "title": "Filed to send activation email",
            "message": "Unfortunately, we were unable to send the activation email to your email address. Please try again later"
        })