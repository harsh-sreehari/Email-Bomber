from fastapi import FastAPI, Form
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage

app = FastAPI()

class EmailRequest(BaseModel):
    sender_email: str
    sender_password: str  # Use App Password for Gmail
    receiver_email: str
    subject: str
    message: str


@app.post("/send_email/")
async def send_email(request: EmailRequest):
    try:
        # Create email
        msg = EmailMessage()
        msg.set_content(request.message)
        msg["Subject"] = request.subject
        msg["From"] = request.sender_email
        msg["To"] = request.receiver_email

        # Connect to Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as mail_server:
            mail_server.ehlo()
            mail_server.starttls()
            mail_server.login(request.sender_email, request.sender_password)
            mail_server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully ✅"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
